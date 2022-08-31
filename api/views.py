from datetime import datetime
from django.db.models import Q
from django.shortcuts import get_object_or_404
import pytz
from rest_framework import permissions, status, viewsets
from rest_framework.generics import (
    CreateAPIView, 
    ListAPIView, 
    ListCreateAPIView, 
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView,)
from rest_framework.parsers import JSONParser, FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from .algorithm import RankCalibration
from .models import (
    Court, 
    CourtAddress, 
    GameSession,
    Guest, 
    NotificationGameSession,
    Survey,
    User,
    restrict_guest_amount_on_game_session,
    update_game_session_confirmed_field,
    update_game_session_full_field,
    update_wins_losses_field,)
from .permissions import IsOwnerOrReadOnly, GuestPermission
from .serializers import (
    CourtSerializer,
    CourtAddressSerializer,
    GameSessionSerializer,
    GuestSerializer,
    ProfileSerializer,
    UserDetailSerializer,
    NotificationGameSessionSerializers,
    SurveySerializer,
    SurveyResponseSerializer,)


def welcome(request):
    return Response({
        'team': 'Team Swan Lake',
        'description': 'Welcome to our app 👋'
    })


# ----- Game Sessions ------
class ListCreateGameSession(ListCreateAPIView):
    serializer_class = GameSessionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = GameSession.objects.filter(
            datetime__gte=datetime.now(pytz.timezone('America/New_York')),
            confirmed=False, 
            full=False
        ).exclude(
            host=self.request.user).exclude(
            guest__user=self.request.user)

        park_search = self.request.query_params.get("location-id")
        if park_search is not None:
            queryset = queryset.filter(location__id__icontains=park_search)
        date_search = self.request.query_params.get("date")
        if date_search is not None:
            queryset = queryset.filter(datetime__icontains=date_search)
        match_type_search = self.request.query_params.get("match-type")
        if match_type_search is not None:
            queryset = queryset.filter(match_type__icontains=match_type_search)
        session_type_search = self.request.query_params.get("session-type")
        if session_type_search is not None:
            queryset = queryset.filter(session_type__icontains=session_type_search)

        return queryset.order_by("datetime")

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)
    
class RetrieveUpdateDestroyGameSession(RetrieveUpdateDestroyAPIView):
    queryset = GameSession.objects.all()
    serializer_class = GameSessionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)


# ----- Guests ------
class GuestViewSet(viewsets.ModelViewSet):
    serializer_class = GuestSerializer
    permission_classes = (GuestPermission,)
    lookup_url_kwarg = 'guest_pk' 

    def get_queryset(self):
        queryset = Guest.objects.filter(game_session = self.kwargs.get('pk'))
        return queryset

    def perform_create(self, serializer):
        game_session_instance = get_object_or_404(GameSession, pk=self.kwargs.get('pk'))
        restrict_guest_amount_on_game_session(game_session_instance.pk)
        serializer.save(user=self.request.user, game_session=game_session_instance)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        game_session_pk = instance.game_session.pk
        update_game_session_confirmed_field(game_session_pk)
        update_game_session_full_field(game_session_pk)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        instance = get_object_or_404(Guest, user=self.request.user,
            game_session=self.kwargs.get('pk'))
        game_session_pk = instance.game_session.pk
        self.perform_destroy(instance)

        update_game_session_confirmed_field(game_session_pk)
        update_game_session_full_field(game_session_pk)

        return Response(status=status.HTTP_204_NO_CONTENT)


# ----- Courts ------
class ListCreateCourt(ListCreateAPIView):
    queryset = Court.objects.all()
    serializer_class = CourtSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

class ListCreateCourtAddress(APIView):
    serializer_class = CourtAddressSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, *args, **kwargs):
        court = get_object_or_404(Court, pk=self.kwargs.get('pk'))
        serializer = CourtAddressSerializer(court.address)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch (self, request, **kwargs):
        court = get_object_or_404(Court, pk=self.kwargs.get('pk'))
        serializer = CourtAddressSerializer(court.address, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post (self, request, **kwargs):
        court_instance = get_object_or_404(Court, pk=self.kwargs.get('pk'))
        court_address = CourtAddress.objects.create(
                court=court_instance,
                address1=request.data['address1'],
                address2=request.data['address2'],
                city=request.data['city'],
                state=request.data['state'],
                zipcode=request.data['zipcode']
        )
        serializer = CourtAddressSerializer(court_address)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


# ------ Profiles ------
class ListCreateUpdateProfile(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    parser_classes = [JSONParser, FileUploadParser]

    def get(self, request):
        user = self.request.user
        update_wins_losses_field(user)
        profile = request.user.profile
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch (self, request, **kwargs):
        self.get(request)
        profile = request.user.profile
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            if bool(request.data['ntrp_rating']) == True:
                RankCalibration(request.data['ntrp_rating'], self.request.user.id)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ----- Users -----
class UserDetail(RetrieveUpdateAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
    lookup_field = 'username'

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        update_wins_losses_field(user)
        queryset = User.objects.filter(username=user)
        return queryset

class MyGamesList(ListAPIView):
    serializer_class = GameSessionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,]
    lookup_field = 'username'

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        update_wins_losses_field(user)
        my_games = GameSession.objects.filter(
            datetime__gte=datetime.now(pytz.timezone('America/New_York')))
    
        my_games_search = self.request.query_params.get("my-games")
        if my_games_search is not None:
            if my_games_search == "AllConfirmed":
                my_games = my_games.filter(confirmed=True, guest__isnull=False,)
                my_host_confirmed_games = my_games.filter(host=user)
                my_guest_confirmed_games = my_games.filter(guest__user=user, guest__status='Accepted')
                my_games = my_host_confirmed_games.union(my_guest_confirmed_games, all=False)
            elif my_games_search == "HostUnconfirmed":
                my_games = my_games.filter(host=user, confirmed=False, guest__status='Pending').distinct()
            elif my_games_search == "GuestPending":
                my_games = my_games.filter(
                    guest__user=user,
                    guest__status='Pending', 
                    confirmed=False)
            elif my_games_search == "HostNoGuest":
                my_games = my_games.filter(
                    host=user,
                    confirmed=False)
                my_games = my_games.filter(~Q(guest__status="Pending"))
                my_games = my_games.filter(~Q(guest__status="Accepted"))
                my_games = my_games.filter(~Q(guest__status="Rejected"))
                my_games = my_games.filter(~Q(guest__status="Wait Listed"))
            elif my_games_search == "HostNotPendingUnconfirmedDoubles":
                my_games = my_games.filter(
                    host=user,
                    match_type="Doubles", 
                    confirmed=False)
                my_games = my_games.filter(~Q(guest__status="Pending"))
            elif my_games_search == "GuestAcceptedUnconfirmedDoubles":
                my_games = my_games.filter(
                    guest__user=user,
                    guest__status="Accepted",
                    match_type="Doubles", 
                    confirmed=False)
            elif my_games_search == "MyPreviousGames":
                my_games = GameSession.objects.filter(
                    datetime__lte=datetime.now(pytz.timezone('America/New_York')),
                    confirmed=True)
                previous_host_confirmed_games = my_games.filter(host=user)
                previous_guest_confirmed_games = my_games.filter(
                    guest__user=user, guest__status='Accepted')
                my_games = previous_host_confirmed_games.union(
                    previous_guest_confirmed_games, all=False)
                return my_games.order_by("-datetime")
        return my_games.order_by("datetime")


# ----- Notifications -----
class CheckNotificationGameSession(ListAPIView):
    serializer_class = NotificationGameSessionSerializers
    permission_classes = [permissions.IsAuthenticated,]

    def get_queryset(self):
        queryset = NotificationGameSession.objects.filter(
            reciever=self.request.user,
            read=False)
        for query in queryset:
            query.read = True
            query.save()
        return queryset

class CountNotificationGameSession(ListAPIView):
    serializer_class = NotificationGameSessionSerializers
    permission_classes = [permissions.IsAuthenticated,]

    def get_queryset(self):
        queryset = NotificationGameSession.objects.filter(
            reciever=self.request.user,
            read=False)
        return queryset

class AllNotificationGameSession(ListAPIView):
    serializer_class = NotificationGameSessionSerializers
    permission_classes = [permissions.IsAuthenticated,]

    def get_queryset(self):
        queryset = NotificationGameSession.objects.filter(reciever=self.request.user)
        return queryset


# ----- Surveys -----
class ListCreateSurvey(ListCreateAPIView):
    serializer_class = SurveySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = Survey.objects.filter(game_session_id=self.kwargs.get('session_pk'))
        return queryset

    def perform_create(self, serializer):
        game_session_instance = get_object_or_404(GameSession, pk=self.kwargs.get('session_pk'))
        respondent = self.request.user
        serializer.save(game_session=game_session_instance, respondent=respondent)

class CreateSurveyResponse(CreateAPIView):
    serializer_class = SurveyResponseSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        survey = get_object_or_404(Survey,
            respondent=self.request.user,
            game_session=self.kwargs.get('session_pk'))
        serializer.save(survey=survey)

from datetime import datetime
import pytz
from functools import partial
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from rest_framework import permissions, status, views, viewsets
from rest_framework.views import APIView
from django.views.generic import TemplateView
from rest_framework.parsers import JSONParser, FileUploadParser
from rest_framework.decorators import permission_classes, api_view
from .permissions import IsOwnerOrReadOnly, IsOwner, GuestPermission, IsUserOwnerOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import (
    CourtSerializer, 
    CourtAddressSerializer, 
    GameSessionSerializer, 
    GuestSerializer, 
    ProfileSerializer, 
    UserDetailSerializer,
    NotificationGameSessionSerializers,
    SurveySerializer,
    SurveyResponseSerializer,
    )

from rest_framework.generics import (
    CreateAPIView, 
    DestroyAPIView, 
    ListAPIView, 
    ListCreateAPIView, 
    RetrieveUpdateDestroyAPIView, 
    RetrieveUpdateAPIView,
)

from .models import (
    User, 
    GameSession, 
    Court, 
    CourtAddress, 
    UserAddress, 
    Guest, 
    Profile, 
    AddressModelMixin,
    NotificationGameSession,
    Survey,
    SurveyResponse,
    restrict_guest_amount_on_game_session,
    update_game_session_confirmed_field,
    update_game_session_full_field,
    update_wins_losses_field,
)


def welcome(request):
    return Response({
        'team': 'Team Swan Lake',
        'description': 'Welcome to our app 👋'
    })

class ListCreateGameSession(ListCreateAPIView):
    serializer_class = GameSessionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        # filter all games session objects to show only future games
        queryset = GameSession.objects.filter(
            datetime__gte=datetime.now(pytz.timezone('America/New_York')),
            confirmed=False, full=False)

        # Allows users to add search params to query for specific results
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

        return queryset.order_by("datetime").exclude(
            host=self.request.user).exclude(guest__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)
    
class RetrieveUpdateDestroyGameSession(RetrieveUpdateDestroyAPIView):
    queryset = GameSession.objects.all()
    serializer_class = GameSessionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)

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

        # Two lines added to override
        game_session_pk = instance.game_session.pk
        update_game_session_confirmed_field(game_session_pk)
        update_game_session_full_field(game_session_pk)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


    def delete(self, request, *args, **kwargs):
        instance = get_object_or_404(Guest, user=self.request.user, game_session=self.kwargs.get('pk'))
        game_session_pk = instance.game_session.pk
        self.perform_destroy(instance)
        update_game_session_confirmed_field(game_session_pk)
        update_game_session_full_field(game_session_pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

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

class ListCreateUpdateProfile(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    parser_classes = [JSONParser, FileUploadParser]

    # This methods checks for a user profile, if one exists, it returns the profile, if one does not exist, it creates one (with default ntrp_rating of 2.5). This eliminates the need for a post method override.
    def get(self, request):
        update_wins_losses_field(self)
        profile = request.user.profile
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch (self, request, **kwargs):
        self.get(request)
        profile = request.user.profile
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetail(RetrieveUpdateAPIView):
    serializer_class = UserDetailSerializer
    # REMOVED IsUserOwnerOrReadOnly permissions for testing later
    permission_classes = [permissions.IsAuthenticated, ]
    lookup_field = 'username'

    def get_queryset(self):
        queryset = User.objects.filter(username=self.kwargs['username'])
        return queryset

# Returns confirmed upcoming games where user = host or guest
class MyConfirmedGameSessions(ListAPIView):
    serializer_class = GameSessionSerializer
    permission_classes = [permissions.IsAuthenticated,]

    def get_queryset(self):
        upcoming_confirmed_games = GameSession.objects.filter(
            datetime__gte=datetime.now(pytz.timezone('America/New_York')),
            confirmed=True)
        confirmed_games_as_host = upcoming_confirmed_games.filter(
            host=self.request.user)
        confirmed_games_as_guest = upcoming_confirmed_games.filter(
            guest__user=self.request.user,
            guest__status='Accepted') 
        all_confirmed_games = confirmed_games_as_host.union(confirmed_games_as_guest, all=False)
        return all_confirmed_games.order_by("datetime")

# Returns confirmed upcoming games where user = host
class MyConfirmedHostGameSessions(ListAPIView):
    serializer_class = GameSessionSerializer
    permission_classes = [permissions.IsAuthenticated,]

    def get_queryset(self):
        upcoming_confirmed_games = GameSession.objects.filter(
            datetime__gte=datetime.now(pytz.timezone('America/New_York')),
            confirmed=True)
        confirmed_games_as_host = upcoming_confirmed_games.filter(
            host=self.request.user)
        return confirmed_games_as_host.order_by("datetime")

# Returns confirmed upcoming games where user = guest
class MyConfirmedGuestGameSessions(ListAPIView):
    serializer_class = GameSessionSerializer
    permission_classes = [permissions.IsAuthenticated,]

    def get_queryset(self):
        upcoming_confirmed_games = GameSession.objects.filter(
            datetime__gte=datetime.now(pytz.timezone('America/New_York')),
            confirmed=True)
        confirmed_games_as_guest = upcoming_confirmed_games.filter(
            guest__user=self.request.user,
            guest__status='Accepted') 
        return confirmed_games_as_guest.order_by("datetime")

# Returns open upcoming games where user = host or guest
class MyOpenGameSessions(ListAPIView):
    serializer_class = GameSessionSerializer
    permission_classes = [permissions.IsAuthenticated,]

    def get_queryset(self):
        upcoming_open_games = GameSession.objects.filter(
            datetime__gte=datetime.now(pytz.timezone('America/New_York')),
            confirmed=False)
        open_games_as_host = upcoming_open_games.filter(
            host=self.request.user)
        open_games_as_guest = upcoming_open_games.filter(
            guest__user=self.request.user,
            guest__status='Accepted')
        all_open_games = open_games_as_host.union(open_games_as_guest, all=False)
        return all_open_games.order_by("datetime")

# Returns open upcoming games where user = host
class MyOpenHostGameSessions(ListAPIView):
    serializer_class = GameSessionSerializer
    permission_classes = [permissions.IsAuthenticated,]
    
    def get_queryset(self):
        upcoming_open_games = GameSession.objects.filter(
            datetime__gte=datetime.now(pytz.timezone('America/New_York')),
            confirmed=False)
        open_games_as_host = upcoming_open_games.filter(
            host=self.request.user)
        return open_games_as_host.order_by("datetime")

# Returns open upcoming games where user = guest
class MyOpenGuestGameSessions(ListAPIView):
    serializer_class = GameSessionSerializer
    permission_classes = [permissions.IsAuthenticated,]

    def get_queryset(self):
        upcoming_open_games = GameSession.objects.filter(
            datetime__gte=datetime.now(pytz.timezone('America/New_York')),
            confirmed=False)
        open_games_as_guest = upcoming_open_games.filter(
            guest__user=self.request.user,
            guest__status='Accepted')
        return open_games_as_guest.order_by("datetime")

class MyGamesList(ListAPIView):
    serializer_class = GameSessionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,]
    lookup_field = 'username'

    def get_queryset(self):
        my_games = GameSession.objects.filter(
            datetime__gte=datetime.now(pytz.timezone('America/New_York')))
    
        my_games_search = self.request.query_params.get("my-games")
        if my_games_search is not None:
            #User's Confirmed Games as Guest and Host
            if my_games_search == "AllConfirmed":
                my_games = my_games.filter(confirmed=True, guest__isnull=False,)
                my_host_confirmed_games =  my_games.filter(host=self.request.user)
                my_guest_confirmed_games = my_games.filter(guest__user=self.request.user, guest__status='Accepted')
                my_games = my_host_confirmed_games.union(my_guest_confirmed_games, all=False)
            # unconfirmed games that I host that have a pending request
            elif my_games_search == "HostUnconfirmed":
                my_games = my_games.filter(host=self.request.user, confirmed=False, guest__status='Pending').distinct()
            #games that I have requested to join and those requests haven't been accepted/rejected yet, aka pending sent requests
            elif my_games_search == "GuestPending":
                my_games = my_games.filter(
                    guest__user=self.request.user, 
                    guest__status='Pending', 
                    confirmed=False)
            # games that I host that have no guests (pending or accepted, etc) so that I can delete this game session and no one needs to be notified. I could also edit this game       
            elif my_games_search == "HostNoGuest":
                my_games = my_games.filter(
                    host=self.request.user, 
                    confirmed=False)
                my_games = my_games.filter(~Q(guest__status="Pending"))
                my_games = my_games.filter(~Q(guest__status="Accepted"))
                my_games = my_games.filter(~Q(guest__status="Rejected"))
                my_games = my_games.filter(~Q(guest__status="Wait Listed"))
            # doubles games that I host with other accepted guest but not confirmed yet and No pending guest
            elif my_games_search == "HostNotPendingUnconfirmedDoubles":
                my_games = my_games.filter(
                    host=self.request.user,
                    match_type="Doubles", 
                    confirmed=False)
                #this filters for guest_status that does not equal pending
                my_games = my_games.filter(~Q(guest__status="Pending"))
            # Doubles games that I am an accepted guest (not the host), but aren't confirmed yet. So I could cancel my request to join this game after I'm accepted
            elif my_games_search == "GuestAcceptedUnconfirmedDoubles":
                my_games = my_games.filter(
                    guest__user=self.request.user,
                    guest__status="Accepted",
                    match_type="Doubles", 
                    confirmed=False)
            # list of my previous games
            elif my_games_search == "MyPreviousGames":
                username = get_object_or_404(User, username=self.kwargs['username'])
                my_games = GameSession.objects.filter(
                    datetime__lte=datetime.now(pytz.timezone('America/New_York')))
                my_games = my_games.filter(confirmed=True, guest__isnull=False,)
                previous_host_confirmed_games =  my_games.filter(host=username)
                previous_guest_confirmed_games = my_games.filter(
                    guest__user=username, guest__status='Accepted')
                my_games = previous_host_confirmed_games.union(
                    previous_guest_confirmed_games, all=False)
                return my_games.order_by("-datetime")
        return my_games.order_by("datetime")

# Returns list of notifications that called once
class CheckNotificationGameSession(ListAPIView):
    serializer_class = NotificationGameSessionSerializers
    permission_classes = [permissions.IsAuthenticated,]

    def get_queryset(self):
        queryset = NotificationGameSession.objects.filter(
            reciever=self.request.user,
            read=False
            )
        #Change read status to True so get can only be called once on the notification
        for query in queryset:
            query.read = True
            query.save()

        return queryset

# Returns list of notifications
class CountNotificationGameSession(ListAPIView):
    serializer_class = NotificationGameSessionSerializers
    permission_classes = [permissions.IsAuthenticated,]

    def get_queryset(self):
        queryset = NotificationGameSession.objects.filter(
            reciever=self.request.user,
            read=False
            )

        return queryset

# Returns list of all notifications
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
        survey = get_object_or_404(Survey, respondent=self.request.user, game_session=self.kwargs.get('session_pk'))
        serializer.save(survey=survey)

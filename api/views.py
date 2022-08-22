from datetime import datetime
import pytz
from functools import partial
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from rest_framework import permissions, status, views, viewsets
from rest_framework.views import APIView
from django.views.generic import TemplateView
from rest_framework.decorators import permission_classes, api_view
from .permissions import IsOwnerOrReadOnly, IsOwner, GuestPermission
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
    )

from rest_framework.generics import (
    CreateAPIView, 
    DestroyAPIView, 
    ListAPIView, 
    ListCreateAPIView, 
    RetrieveUpdateDestroyAPIView, 
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
    restrict_amount,
    check_game_session_confirm_criteria,
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
        queryset = GameSession.objects.filter(date__gte=datetime.now(pytz.timezone('America/New_York')))

        # Allows users to add search params to query for specific results
        park_search = self.request.query_params.get("park-name")
        if park_search is not None:
            queryset = queryset.filter(location__park_name__icontains=park_search)
        date_search = self.request.query_params.get("date")
        if date_search is not None:
            queryset = queryset.filter(date__icontains=date_search)
        match_type_search = self.request.query_params.get("match-type")
        if match_type_search is not None:
            queryset = queryset.filter(match_type__icontains=match_type_search)
        session_type_search = self.request.query_params.get("session-type")
        if session_type_search is not None:
            queryset = queryset.filter(session_type__icontains=session_type_search)

        return queryset.order_by("date","time")

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)
    
class RetrieveUpdateDestroyGameSession(RetrieveUpdateDestroyAPIView):
    queryset = GameSession.objects.all()
    serializer_class = GameSessionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        check_game_session_confirm_criteria(instance.pk)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class GuestViewSet(viewsets.ModelViewSet):
    serializer_class = GuestSerializer
    permission_classes = (GuestPermission,)
    lookup_url_kwarg = 'guest_pk' 

    def get_queryset(self):
        queryset = Guest.objects.filter(game_session = self.kwargs.get('pk'))
        return queryset

    def perform_create(self, serializer):
        game_session_instance = get_object_or_404(GameSession, pk=self.kwargs.get('pk'))
        restrict_amount(game_session_instance.id)
        serializer.save(user=self.request.user, game_session=game_session_instance)

class ListCreateCourt(ListCreateAPIView):
    queryset = Court.objects.all()
    serializer_class = CourtSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

class ListCreateCourtAddress(ListCreateAPIView):
    serializer_class = CourtAddressSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = CourtAddress.objects.filter(court_id=self.kwargs.get('pk'))
        return queryset
    
    def perform_create(self, serializer):
        court = get_object_or_404(Court, pk=self.kwargs.get('pk'))
        serializer.save(court=court)

class ListCreateUpdateProfile(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    # This methods checks for a user profile, if one exists, it returns the profile, if one does not exist, it creates one (with default ntrp_rating of 2.5). This eliminates the need for a post method override.
    def get(self, request):
        try:
            profile = request.user.profile
            serializer = ProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            create_profile = Profile(user=request.user)
            create_profile.save()
            serializer = ProfileSerializer(create_profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def patch (self, request, **kwargs):
        self.get(request)
        profile = request.user.profile
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetail(ListAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated,]

    def get_queryset(self):
        queryset = User.objects.filter(username=self.kwargs['username'])
        return queryset

# Returns confirmed games where user = host | guest
class MyConfirmedGameSessions(ListAPIView):
    serializer_class = GameSessionSerializer
    permission_classes = [permissions.IsAuthenticated,]

    def get_queryset(self):
        queryset = GameSession.objects.filter(
            Q(host=self.request.user, guest__status='Accepted') |
            Q(guest__user=self.request.user, guest__status='Accepted'))
        # Only show upcoming games
        queryset = queryset.filter(date__gte=datetime.now(pytz.timezone('America/New_York')))
        return queryset.order_by("date","time")

# Returns confirmed games where user = host
class MyConfirmedHostGameSessions(ListAPIView):
    serializer_class = GameSessionSerializer
    permission_classes = [permissions.IsAuthenticated,]

    def get_queryset(self):
        queryset = GameSession.objects.filter(
            host=self.request.user, 
            guest__status='Accepted')
        # Only show upcoming games
        queryset = queryset.filter(date__gte=datetime.now(pytz.timezone('America/New_York')))
        return queryset.order_by("date","time")

# Returns confirmed games where user = guest
class MyConfirmedGuestGameSessions(ListAPIView):
    serializer_class = GameSessionSerializer
    permission_classes = [permissions.IsAuthenticated,]

    def get_queryset(self):
        queryset = GameSession.objects.filter(
            guest__user=self.request.user, 
            guest__status='Accepted')
        # Only show upcoming games
        queryset = queryset.filter(date__gte=datetime.now(pytz.timezone('America/New_York')))
        return queryset.order_by("date","time")

# Returns open games where user = host | guest
class MyOpenGameSessions(ListAPIView):
    serializer_class = GameSessionSerializer
    permission_classes = [permissions.IsAuthenticated,]

    def get_queryset(self):
        queryset = GameSession.objects.filter(
            Q(host=self.request.user, guest__status='Pending') | 
            Q(guest__user=self.request.user, guest__status='Pending'))
        # Only show upcoming games
        queryset = queryset.filter(date__gte=datetime.now(pytz.timezone('America/New_York')))
        return queryset.order_by("date","time")

# Returns open games where user = host
class MyOpenHostGameSessions(ListAPIView):
    serializer_class = GameSessionSerializer
    permission_classes = [permissions.IsAuthenticated,]
    
    def get_queryset(self):
        queryset = GameSession.objects.filter(
            host=self.request.user,
            guest__status='Pending')
        # Only show upcoming games
        queryset = queryset.filter(date__gte=datetime.now(pytz.timezone('America/New_York')))
        return queryset.order_by("date","time")

# Returns open games where user = guest
class MyOpenGuestGameSessions(ListAPIView):
    serializer_class = GameSessionSerializer
    permission_classes = [permissions.IsAuthenticated,]

    def get_queryset(self):
        queryset = GameSession.objects.filter(
            guest__user=self.request.user, 
            guest__status='Pending')
        # Only show upcoming games
        queryset = queryset.filter(date__gte=datetime.now(pytz.timezone('America/New_York')))
        return queryset.order_by("date","time")

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
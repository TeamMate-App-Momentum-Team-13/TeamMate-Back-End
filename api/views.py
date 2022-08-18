from datetime import datetime
import pytz
from functools import partial
from django.shortcuts import render, get_object_or_404
from rest_framework import permissions, status, views, viewsets
from rest_framework.views import APIView
from django.views.generic import TemplateView
from rest_framework.decorators import permission_classes, api_view
from .permissions import IsOwnerOrReadOnly, IsOwner, GuestPermission
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import GameSessionSerializer, GuestSerializer, ProfileSerializer, UserDetailSerializer

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
    AddressModelMixin
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

class GuestViewSet(viewsets.ModelViewSet):
    serializer_class = GuestSerializer
    permission_classes = (GuestPermission,)
    lookup_url_kwarg = 'guest_pk' 

    def get_queryset(self):
        queryset = Guest.objects.filter(game_session = self.kwargs.get('pk'))
        return queryset

    def perform_create(self, serializer):
        game_session_instance = get_object_or_404(GameSession, pk=self.kwargs.get('pk'))
        serializer.save(user=self.request.user, game_session=game_session_instance)
        
class ListCreateUpdateProfile(APIView):
    permission_classes = (IsOwnerOrReadOnly,)

    def get(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request): 
        user = self.request.user
        if self.request.data == {}:
            profile = Profile(user=user)
        else:
            ntrp_rating = self.request.data["ntrp_rating"]
            profile = Profile(user=user, ntrp_rating=ntrp_rating)
        profile.save()
        serializer = ProfileSerializer(profile, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def patch (self, request, **kwargs):
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

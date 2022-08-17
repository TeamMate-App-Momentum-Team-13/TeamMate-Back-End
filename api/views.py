from functools import partial
from django.shortcuts import render, get_object_or_404
from rest_framework import permissions, status, views, viewsets
from rest_framework.views import APIView
from django.views.generic import TemplateView
from rest_framework.decorators import permission_classes, api_view
from .permissions import IsOwnerOrReadOnly, IsOwner, GuestPermission
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import GameSessionSerializer, GuestSerializer, ProfileSerializer, UserSerializer

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
    queryset = GameSession.objects.all()
    serializer_class = GameSessionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

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
        
class CreateProfile(APIView): 

    def get(self, request):
        pass
    
    def post(self, request):
        user = self.request.user
        if self.request.data == {}:
            profile = Profile(user=user)
        else:
            ntrp_rating = self.request.data["ntrp_rating"]
            profile = Profile(user=user, ntrp_rating=ntrp_rating)
        profile.save()
        serializer = ProfileSerializer(profile, context={'request': request})
        return Response(serializer.data, status=201)

    def patch(self, request):
        pass
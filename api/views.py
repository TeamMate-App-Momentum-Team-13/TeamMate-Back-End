from django.shortcuts import render, get_object_or_404
from rest_framework import permissions
from .permissions import IsOwnerOrReadOnly, IsOwner
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

class ListCreateGuest(ListCreateAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer

    def perform_create(self, serializer):
        game_session_instance = get_object_or_404(GameSession, pk=self.kwargs.get('pk'))
        serializer.save(user=self.request.user, game_session=game_session_instance)
        
class CreateProfile(APIView): 

    def get(self, request):
        pass
    
    def post(self, request, **kwargs):
        user = self.request.user.pk
        print(user)
        profile = Profile({"user": str(user)})
        serializer = ProfileSerializer(profile, context={'request': request})
        return Response(serializer.data, status=201)
    
    # def post(self, request, **kwargs):
    #     user = self.request.user
    #     profile = get_object_or_404(Profile, pk=self.kwargs['pk'])
    #     p_user = get_object_or_404(User, pk=self.kwargs['pk'])
    #     user.profile.add(p_user)
    #     serializer = UserSerializer(user, context={'request': request})
    #     return Response(serializer.data, status=201)

    def patch(self, request):
        pass

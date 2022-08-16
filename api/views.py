from django.shortcuts import render, get_object_or_404
from rest_framework import permissions
from rest_framework.views import APIView
from .permissions import IsOwnerOrReadOnly, IsOwner
from rest_framework.response import Response
from .serializers import GameSessionSerializer, GuestSerializer

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
    serializer_class = GuestSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = Guest.objects.filter(game_session =self.kwargs.get('pk'))
        return queryset

    def perform_create(self, serializer):
        game_session_instance = get_object_or_404(GameSession, pk=self.kwargs.get('pk'))
        serializer.save(user=self.request.user, game_session=game_session_instance)
        
# class GameSessionGuest(RetrieveUpdateDestroyAPIView):
#     queryset = Guest.objects.all()
#     serializer_class = GuestSerializer
#     lookup_url_kwarg = 'guest_pk'

class GameSessionGuest(APIView):
    lookup_url_kwarg = 'guest_pk'

    def get(self, request, **kwargs):
        guest_detail = get_object_or_404(Guest, pk=self.kwargs.get('guest_pk'))
        serializer = GuestSerializer(guest_detail, many=False)
        return Response(serializer.data)


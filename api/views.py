from django.shortcuts import render
from rest_framework.generics import (
    CreateAPIView, 
    DestroyAPIView, 
    ListAPIView, 
    ListCreateAPIView, 
    RetrieveUpdateDestroyAPIView, 
)
from rest_framework.response import Response

from .models import User, GameSession, Court, CourtAddress, UserAddress, Guest, Profile, AddressModelMixin

from .serializers import GameSessionSerializer


def welcome(request):
    return Response({
        'team': 'Team Swan Lake',
        'description': 'Welcome to our app 👋'
    })


class ListCreateGameSession(ListCreateAPIView):
    queryset = GameSession.objects.all()
    serializer_class = GameSessionSerializer

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)

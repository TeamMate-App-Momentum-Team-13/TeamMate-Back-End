from pyexpat import model
from rest_framework import serializers
from .models import User, GameSession, Court, CourtAddress, UserAddress, Guest, Profile, AddressModelMixin

class GameSessionSerializer(serializers.ModelSerializer):
    guest = serializers.PrimaryKeyRelatedField(many=True, queryset=Guest.objects.all())

    class Meta:
        model = GameSession
        fields = [
            'id',
            'host',
            'date',
            'time',
            'session_type',
            'match_type',
            'location',
            'guest',
        ]

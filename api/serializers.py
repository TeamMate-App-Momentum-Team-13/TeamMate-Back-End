from pyexpat import model
from rest_framework import serializers
from .models import User, GameSession, Court, CourtAddress, UserAddress, Guest, Profile, AddressModelMixin

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
        ]

class CourtAddressSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CourtAddress
        fields = [
            'id',
            'address1',
            'address2',
            'city',
            'state',
            'zipcode',
            'court',
        ]

class CourtSerializer(serializers.ModelSerializer):

    class Meta:
        model = Court
        fields = [
            'id',
            'park_name',
            'court_count',
            'court_surface',
        ]


class GameSessionSerializer(serializers.ModelSerializer):
    host = serializers.ReadOnlyField(source='user.username')
    # host = serializers.SlugRelatedField(slug_field="username", read_only=True)
    # guest = serializers.PrimaryKeyRelatedField(many=True, queryset=Guest.objects.all())
    guest = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    host_info = UserSerializer(source='host', read_only=True)
    location_info = CourtSerializer(source='location', read_only=True)

    class Meta:
        model = GameSession
        fields = [
            'id',
            'host',
            'host_info',
            'date',
            'time',
            'session_type',
            'match_type',
            'location',
            'location_info',
            'guest',
        ]

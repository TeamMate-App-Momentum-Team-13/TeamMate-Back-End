import profile
from pyexpat import model
from rest_framework import serializers
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
)


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    
    
    class Meta:
        model = Profile
        fields = [
            'id',
            'user',
            'profile_pic',
            'ntrp_rating',
        ]

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'profile',
        ]

class CourtAddressSerializer(serializers.ModelSerializer):
    court = serializers.SlugRelatedField(slug_field="park_name", read_only=True)
    
    class Meta:
        model = CourtAddress
        fields = [
            'id',
            'court',
            'address1',
            'address2',
            'city',
            'state',
            'zipcode',
        ]

class CourtSerializer(serializers.ModelSerializer):
    address = CourtAddressSerializer(read_only=True)

    class Meta:
        model = Court
        fields = [
            'id',
            'park_name',
            'court_count',
            'court_surface',
            'address',
        ]

class GuestSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    game_session = serializers.SlugRelatedField(slug_field="id", read_only=True)
    
    class Meta:
        model = Guest
        fields = [
            'id',
            'user',
            'game_session',
            'status',
        ]

class GameSessionSerializer(serializers.ModelSerializer):
    host = serializers.SlugRelatedField(slug_field="username", read_only=True)
    guest = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    host_info = UserSerializer(source='host', read_only=True)
    location_info = CourtSerializer(source='location', read_only=True)
    guest_info = GuestSerializer(source='guest', many=True, read_only=True)

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
            'guest_info',
            'confirmed'
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    game_session = GameSessionSerializer(many=True, read_only=True)
    guest = GuestSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'profile',
            'game_session',
            'guest',
        ]

class NotificationGameSessionSerializers(serializers.ModelSerializer):

    class Meta:
        model = NotificationGameSession
        fields = [
            'id',
            'sender',
            'reciever',
            'message',
            'game_session',
            'read',
        ]
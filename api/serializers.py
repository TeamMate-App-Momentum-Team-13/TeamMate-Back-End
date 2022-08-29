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
    Survey,
    SurveyResponse,
)


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    profile_id = serializers.ReadOnlyField(source='id')
    
    class Meta:
        model = Profile
        fields = [
            'profile_id',
            'user',
            'profile_pic',
            'ntrp_rating',
            'wins',
            'profile_image_file',
        ]

    def update(self, instance, validated_data):
      if "file" in self.initial_data:
            file = self.initial_data.get("file")
            instance.profile_image_file.save(file.name, file, save=True)
            return instance
      # this call to super is to make sure that update still works for other fields
      return super().update(instance, validated_data)

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    user_id = serializers.ReadOnlyField(source='id')
    class Meta:
        model = User
        fields = [
            'user_id',
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
    user_info = UserSerializer(source='user', read_only=True)
    guest_id = serializers.ReadOnlyField(source='id')

    class Meta:
        model = Guest
        fields = [
            'guest_id',
            'status',
            'game_session',
            'user',
            'user_info',
        ]

class GameSessionSerializer(serializers.ModelSerializer):
    host = serializers.SlugRelatedField(slug_field="username", read_only=True)
    guest = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    host_info = UserSerializer(source='host', read_only=True)
    location_info = CourtSerializer(source='location', read_only=True)
    guest_info = GuestSerializer(source='guest', many=True, read_only=True)
    game_session_id = serializers.ReadOnlyField(source='id')

    class Meta:
        model = GameSession
        fields = [
            'game_session_id',
            'confirmed',
            'full',
            'datetime',
            'endtime',
            'session_type',
            'match_type',
            'host',
            'host_info',
            'guest',
            'guest_info',
            'location',
            'location_info',
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

# ----- Surveys -----
class SurveyResponseSerializer(serializers.ModelSerializer):
    survey = serializers.SlugRelatedField(slug_field="id", read_only=True)
    about_user_username = serializers.PrimaryKeyRelatedField(source='about_user.username', read_only=True)
    about_court_name = serializers.PrimaryKeyRelatedField(source='about_court.park_name', read_only=True)

    class Meta:
        model = SurveyResponse
        fields = [
            'id',
            'survey',
            'about_user',
            'about_user_username',
            'about_court',
            'about_court_name',
            'response',
        ]

class SurveySerializer(serializers.ModelSerializer):
    respondent = serializers.SlugRelatedField(slug_field="username", read_only=True)
    game_session = serializers.SlugRelatedField(slug_field="id", read_only=True)

    class Meta:
        model = Survey
        fields = [
            'id',
            'respondent',
            'game_session',
        ]

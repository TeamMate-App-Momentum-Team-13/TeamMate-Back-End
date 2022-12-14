from datetime import timedelta, datetime
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
import pytz
from .algorithm import rank_calibration, determine_game_type
from .notifications import created_guest_notification, updated_guest_notification


class User(AbstractUser):

    REQUIRED_FIELDS = ['first_name', 'last_name']
    def __str__(self):
        return self.username

    def __repr__(self):
        return f'<User username={self.username} pk={self.pk}>'


class BaseModel(models.Model):
    created_at = models.DateTimeField(db_index=True, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Profile(BaseModel):
    TWOFIVE = '2.5'
    THREE = '3'
    THREEFIVE = '3.5'
    FOUR = '4'
    FOURFIVE = '4.5'
    FIVE = '5'
    FIVEFIVE = '5.5'
    SIX = '6'
    SIXFIVE = '6.5'
    SEVEN = '7'
    RATE_CHOICES = [
        (TWOFIVE, '2.5'),
        (THREE, '3'),
        (THREEFIVE, '3.5'),
        (FOUR, '4'),
        (FOURFIVE, '4.5'),
        (FIVE, '5'),
        (FIVEFIVE, '5.5'),
        (SIX, '6'),
        (SIXFIVE, '6.5'),
        (SEVEN, '7'),
    ]

    GOLD = '#daa520'
    SILVER = '#a9a9a9'
    BRONZE = '#904d00'
    RANK_CHOICES = [
        (GOLD, '#daa520'),
        (SILVER, '#a9a9a9'),
        (BRONZE, '#904d00'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_pic = models.TextField(blank=True, null=True)
    profile_image_file = models.ImageField(upload_to='profile_images', null=True, blank=True, max_length=600)
    ntrp_rating = models.CharField(max_length=10, choices=RATE_CHOICES, default=TWOFIVE)
    wins_losses = models.CharField(max_length=30, null=True, blank=True)
    teammate_ntrp = models.CharField(max_length=10, choices=RATE_CHOICES, default=TWOFIVE)
    teammate_rank = models.CharField(max_length=10, choices=RANK_CHOICES, default=BRONZE)

    def __str__(self):
        return f"{self.user}"


class Court(BaseModel):
    HARD_COURT = 'Hard Court'
    GRASS_COURT = 'Grass Court'
    CLAY_COURT = 'Clay Court'
    COURT_CHOICES = [
        (HARD_COURT, 'Hard Court'),
        (GRASS_COURT, 'Grass Court'),
        (CLAY_COURT, 'Clay Court'),
    ]
    park_name = models.CharField(max_length=250)
    court_count = models.PositiveSmallIntegerField(null=True, blank=True)
    court_surface = models.CharField(max_length=250, choices=COURT_CHOICES, default=HARD_COURT)

    def __str__(self):
        return f"{self.park_name}"


class AddressModelMixin(BaseModel):
    address1 = models.CharField(max_length=250, blank=True, null=True)
    address2 = models.CharField(max_length=250, blank=True, null=True)
    city = models.CharField(max_length=250)
    state = models.CharField(max_length=250)
    zipcode = models.CharField(max_length=5)

    def __str__(self):
        return f"{self.address1}, {self.city}, {self.state}, {self.zipcode}"


class UserAddress(AddressModelMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='address')

    def __str__(self):
        return f"{self.user}"


class CourtAddress(AddressModelMixin):
    court = models.OneToOneField(Court, on_delete=models.CASCADE, related_name='address')
    
    def __str__(self):
        return f"{self.court}"


class GameSession(BaseModel):
    CASUAL = 'Casual'
    COMPETITIVE = 'Competitive'
    SESSION_CHOICES = [
        (CASUAL, 'Casual'),
        (COMPETITIVE, 'Competitive'),
    ]

    SINGLES = 'Singles'
    DOUBLES = 'Doubles'
    MATCH_CHOICES = [
        (SINGLES, 'Singles'),
        (DOUBLES, 'Doubles'),
    ]

    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_session')
    datetime = models.DateTimeField(auto_now_add=False)
    endtime = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    session_type = models.CharField(max_length=250, choices=SESSION_CHOICES)
    match_type = models.CharField(max_length=250, choices=MATCH_CHOICES, default=SINGLES)
    location = models.ForeignKey(Court, on_delete=models.CASCADE, related_name='game_session')
    confirmed = models.BooleanField(default=False)
    full = models.BooleanField(default=False)

    def __str__(self):
        return f"Game Session:{self.pk}, Hosted by:{self.host}, {self.match_type}, {self.session_type}"

class Guest(BaseModel):
    
    PENDING = 'Pending'
    WAITLISTED = 'Wait Listed'
    ACCEPTED = 'Accepted'
    REJECTED = 'Rejected'
    HOST = 'Host'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (WAITLISTED, 'Wait Listed'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
        (HOST, 'Host'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='guest')
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='guest')
    status = models.CharField(max_length=250, choices=STATUS_CHOICES, default=PENDING)

    class Meta:
        constraints = [
			models.UniqueConstraint(fields=['user', 'game_session'], name='unique_game_sessoin_follow')
		]

    def __str__(self):
        return f"{self.user},Game Session: {self.game_session},Status: {self.status}"


class NotificationGameSession(BaseModel):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    reciever = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reciever')
    message = models.TextField()
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='game_session', blank=True, null=True)
    read = models.BooleanField(default=False)


class Survey(BaseModel):
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE,
        related_name='survey')
    respondent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='survey')


class SurveyResponse(BaseModel):
    # RE: Q1 - no-show(s)
    NO_SHOW = 'No Show'
    # RE: Q2 - winner(s)
    WINNER = 'Winner'
    # RE: Q3 - blocking a user
    BLOCK_USER = 'Block User'
    # RE: Q4 - court quality
    HIGH_QUALITY = 'High Quality'
    AVERAGE_QUALITY = 'Average Quality'
    POOR_QUALITY = 'Poor Quality'

    RESPONSE_CHOICES = [
        (NO_SHOW, 'No Show'),
        (WINNER, 'Winner'),
        (BLOCK_USER, 'Block User'),
        (HIGH_QUALITY, 'High Quality'),
        (AVERAGE_QUALITY, 'Average Quality'),
        (POOR_QUALITY, 'Poor Quality'),
    ]

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='survey_response')

    # Every instance would have one of these two FK fields populated and the other left Null
    about_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
        related_name='about_user')
    about_court = models.ForeignKey(Court, on_delete=models.CASCADE, null=True, blank=True,
        related_name='about_court')

    response = models.CharField(max_length=25, choices=RESPONSE_CHOICES)


class RankUpdate(BaseModel):
    TWOFIVE = '2.5'
    THREE = '3'
    THREEFIVE = '3.5'
    FOUR = '4'
    FOURFIVE = '4.5'
    FIVE = '5'
    FIVEFIVE = '5.5'
    SIX = '6'
    SIXFIVE = '6.5'
    SEVEN = '7'
    RATE_CHOICES = [
        (TWOFIVE, '2.5'),
        (THREE, '3'),
        (THREEFIVE, '3.5'),
        (FOUR, '4'),
        (FOURFIVE, '4.5'),
        (FIVE, '5'),
        (FIVEFIVE, '5.5'),
        (SIX, '6'),
        (SIXFIVE, '6.5'),
        (SEVEN, '7'),
    ]

    GOLD = '#daa520'
    SILVER = '#a9a9a9'
    BRONZE = '#904d00'
    RANK_CHOICES = [
        (GOLD, '#daa520'),
        (SILVER, '#a9a9a9'),
        (BRONZE, '#904d00'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rankupdate')
    tm_score = models.SmallIntegerField()
    tm_ntrp = models.CharField(max_length=10, choices=RATE_CHOICES, default=TWOFIVE)
    tm_rank = models.CharField(max_length=10, choices=RANK_CHOICES, default=BRONZE)
    created_at = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=Guest)
def notification_created_or_updated_guest_handler(sender, instance, created, *args, **kwargs):
    if created:
        created_guest_notification(instance)
    else: 
        updated_guest_notification(instance)

@receiver(post_save, sender=User)
def user_created_profile_handler(sender, instance, created, *args, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=Profile)
def user_created_profile_handler_update(sender, instance, created, *args, **kwargs):
    if created:
        rank_calibration(instance.ntrp_rating, instance.user.id)

@receiver(post_save, sender=RankUpdate)
def user_created_rank_update_handler(sender, instance, created, *args, **kwargs):
    if created:
        profile = get_object_or_404(Profile, user=instance.user)
        profile.teammate_ntrp=instance.tm_ntrp
        profile.teammate_rank=instance.tm_rank
        profile.save()

@receiver(post_save, sender=SurveyResponse)
def user_created_profile_handler(sender, instance, created, *args, **kwargs):
    if created:
        if instance.response == "Winner":
            determine_game_type(instance)

@receiver(post_save, sender=GameSession)
def notification_created_or_updated_guest_handler(sender, instance, created, *args, **kwargs):
    if created:
        Guest.objects.create(
            user = instance.host,
            game_session = instance,
            status = 'Host'
        )
        instance.endtime = instance.datetime + timedelta(hours=1)
        instance.save()
    else:
        if (instance.datetime + timedelta(hours=1)) != instance.endtime:
        #this is need incase date time is patched 
            instance.endtime = instance.datetime + timedelta(hours=1)
            instance.save()

@receiver(post_delete, sender=Guest)
def notification_for_deleted_guest_handler(sender, instance, *args, **kwargs):
    update_game_session_confirmed_field(instance.game_session.pk)
    update_game_session_full_field(instance.game_session.pk)


def update_game_session_full_field(game_session_pk):
    game_session = GameSession.objects.get(pk=game_session_pk)
    guests = game_session.guest.all()
    guests_count = guests.count()

    if game_session.match_type == 'Singles':
        if guests_count == 4:
            set_full_to_true(game_session)
        else:
            set_full_to_false(game_session)
    elif game_session.match_type == 'Doubles':
        if guests_count == 7:
            set_full_to_true(game_session)
        else:
            set_full_to_false(game_session)

def set_full_to_true(game_session):
    game_session.full = True
    game_session.save()

def set_full_to_false(game_session):
    game_session.full = False
    game_session.save()


def update_game_session_confirmed_field(game_session_pk):
    game_session = GameSession.objects.get(pk=game_session_pk)
    guests = game_session.guest.all()
    accepted_guests_count = guests.filter(status = 'Accepted').count()

    if game_session.match_type == 'Singles':
        if accepted_guests_count == 1:
            set_confirmed_to_true(game_session)
        else:
            set_confirmed_to_false(game_session)
    elif game_session.match_type == 'Doubles':
        if accepted_guests_count == 3:
            set_confirmed_to_true(game_session)
        else:
            set_confirmed_to_false(game_session)

def set_confirmed_to_true(game_session):
    game_session.confirmed = True
    game_session.save()

def set_confirmed_to_false(game_session):
    game_session.confirmed = False
    game_session.save()


def update_wins_losses_field(user):
    games_won = GameSession.objects.filter(
        datetime__lte=datetime.now(pytz.timezone('America/New_York')),
        confirmed=True,
        survey__respondent=user,
        survey__survey_response__about_user=user,
        survey__survey_response__response='Winner')
    games_won_count = games_won.count()

    games_played = GameSession.objects.filter(
        datetime__lte=datetime.now(pytz.timezone('America/New_York')),
        confirmed=True,
        survey__respondent=user)
    games_played_count = games_played.count()

    games_lost_count = games_played_count - games_won_count

    profile = Profile.objects.get(user=user.pk)
    profile.wins_losses = f'{games_won_count} - {games_lost_count}'
    profile.save()

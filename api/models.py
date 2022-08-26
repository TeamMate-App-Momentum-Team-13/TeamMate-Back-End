from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

#signals imports

from django.dispatch import receiver
from django.db.models.signals import (
    post_save,
    post_delete,
    pre_delete,
)

#This is the post_save django signal
@receiver(post_save, sender='api.Guest')
def notification_created_or_updated_guest_handler(sender, instance, created, *args, **kwargs):
    if created:
        print(f"{instance.user.username} is pending for {instance.game_session}")
        NotificationGameSession.objects.create(
            sender=instance.user,
            reciever=instance.game_session.host,
            message=(f"Good news, {instance.user.first_name} would like you join your game on {instance.game_session.date} at {instance.game_session.time}. Please go to MyGames to respond."),
            game_session = instance.game_session,
        )
    else: 
        print("Guest has been updated")
        update_game_session_confirmed_field(instance.game_session.pk)
        if instance.status == "Accepted":
            response = f"Yay! {instance.game_session.host.first_name} has confirmed your game on {instance.game_session.date} at {instance.game_session.time}. You can see all of your confirmed games on the MyGames page."
        elif instance.status == "Rejected":
            response = f"Darn, {instance.game_session.host.first_name} isn't available to play on {instance.game_session.date} anymore, but you can sign up for a different game on the Open Games page."
        else:
            response = f"Your guest request status has changed to {instance.status}"

        NotificationGameSession.objects.create(
            sender=instance.game_session.host,
            reciever=instance.user,
            message=response,
            game_session = instance.game_session,
        )

@receiver(post_save, sender='api.User')
def user_created_profile_handler(sender, instance, created, *args, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_delete, sender='api.Guest')
def notification_for_deleted_guest_handler(sender, instance, *args, **kwargs):
    if instance.status == "Accepted" or instance.status == "Pending":
        print("Accepted guest is deleted")
        NotificationGameSession.objects.create(
            sender=instance.user,
            reciever=instance.game_session.host,
            message=(f"Oh no! {instance.user} can't make it to your game on {instance.game_session.date} at {instance.game_session.time}. We'll add this game to the list of open games so other users can sign up."),
            game_session = instance.game_session,
        )
    else:
        print("Other guest object was deleted")

# @receiver(pre_delete, sender='api.GameSession')
# def notification_for_deleted_game_session_handler(sender, instance, *args, **kwargs):
#     print("Game Session deleted")
    # if instance.guest.count() > 0:
    #     for guest_instance in instance.guest.all():
    #         NotificationGameSession.objects.create(
    #             sender=instance.host,
    #             reciever=guest_instance.user,
    #             message=(f"Oh no, Host canceled game")
    #             # message=(f"Oh no! {instance.host} has cancelled your game on {instance.date} at {instance.time}. You can sign up for a different game on the Open Games page."),
    #         )

def restrict_guest_amount_on_game_session(game_session_pk):
        game_session = GameSession.objects.get(id=game_session_pk)
        if game_session.match_type == 'Singles'and game_session.guest.count() >= 3:
            raise ValidationError(f'Game Session already has maximal amount of Guest({3})')
        elif game_session.match_type == 'Doubles' and game_session.guest.count() >= 6:
            raise ValidationError(f'Game Session already has maximal amount of Guest ({6})')


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
    date = models.DateField()
    time = models.TimeField()
    session_type = models.CharField(max_length=250, choices=SESSION_CHOICES)
    match_type = models.CharField(max_length=250, choices=MATCH_CHOICES, default=SINGLES)
    location = models.ForeignKey(Court, on_delete=models.CASCADE, related_name='game_session')
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"Game Session:{self.pk}, Hosted by:{self.host}, {self.match_type}, {self.session_type}"

class Guest(BaseModel):
    
    PENDING = 'Pending'
    WAITLISTED = 'Wait Listed'
    ACCEPTED = 'Accepted'
    REJECTED = 'Rejected'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (WAITLISTED, 'Wait Listed'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='guest')
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='guest', validators=(restrict_guest_amount_on_game_session, ))
    status = models.CharField(max_length=250, choices=STATUS_CHOICES, default=PENDING)

    class Meta:
        constraints = [
			models.UniqueConstraint(fields=['user', 'game_session'], name='unique_game_sessoin_follow')
		]

    def __str__(self):
        return f"{self.user},Game Session: {self.game_session},Status: {self.status}"

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

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_pic = models.TextField(blank=True, null=True)
    profile_image_file = models.ImageField(upload_to='profile_images', null=True, blank=True, max_length=600)
    ntrp_rating = models.CharField(max_length=10, choices=RATE_CHOICES, default=TWOFIVE)

    def __str__(self):
        return f"{self.user}"

#related name clased when all of them were set to "notificationgamesession"
class NotificationGameSession(BaseModel):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    reciever = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reciever')
    message = models.TextField()
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='game_session', blank=True, null=True)
    read = models.BooleanField(default=False)

# ----- Surveys -----
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

    # Generated from the URL
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='survey_response')

    # Every instance would have one of these two FK fields populated and the other left Null
    about_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
        related_name='about_user')
    about_court = models.ForeignKey(Court, on_delete=models.CASCADE, null=True, blank=True,
        related_name='about_court')

    # Every instance must have a response
    response = models.CharField(max_length=25, choices=RESPONSE_CHOICES)

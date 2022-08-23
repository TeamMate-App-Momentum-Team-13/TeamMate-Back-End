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
            message=(f"You have a new Pending Guest."),
            game_session = instance.game_session,
        )
    else: 
        print("Guest has been updated")
        update_game_session_confirmed_field(instance.game_session.pk)
        NotificationGameSession.objects.create(
            sender=instance.game_session.host,
            reciever=instance.user,
            message=(f"Your guest request status has changed to {instance.status}"),
            game_session = instance.game_session,
        )

@receiver(post_save, sender='api.User')
def user_created_profile_handler(sender, instance, created, *args, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_delete, sender='api.Guest')
def notification_for_deleted_guest_handler(sender, instance, *args, **kwargs):
    if instance.status == "Accepted":
        print("Accepted guest is deleted")
        NotificationGameSession.objects.create(
            sender=instance.user,
            reciever=instance.game_session.host,
            message=(f"{instance.user} has backed out of the game"),
            game_session = instance.game_session,
        )
    else:
        print("Other guest object was deleted")

@receiver(pre_delete, sender='api.GameSession')
def notification_for_deleted_game_session_handler(sender, instance, *args, **kwargs):
    print("Game Session deleted")
    if instance.guest.count() >= 0:
        for guest_instance in instance.guest.all():
            NotificationGameSession.objects.create(
                user=instance.id,
                reciever=guest_instance.user,
                message=(f"{instance.host} has canceled the game"),
            )

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
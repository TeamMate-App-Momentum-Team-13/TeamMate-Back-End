from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
# Comment

class User(AbstractUser):
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='address')

    def __str__(self):
        return f"{self.user_address}"

class CourtAddress(AddressModelMixin):
    court = models.ForeignKey(Court, on_delete=models.CASCADE, related_name='address')
    
    def __str__(self):
        return f"{self.court_address}"

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
        (COMPETITIVE, 'Doubles'),
    ]
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_session')
    date = models.DateField()
    time = models.TimeField()
    session_type = models.CharField(max_length=250, choices=SESSION_CHOICES)
    match_type = models.CharField(max_length=250, choices=MATCH_CHOICES, default=SINGLES)
    locatation = models.ForeignKey(Court, on_delete=models.CASCADE, related_name='game_session')

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
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='guest')
    status = models.CharField(max_length=250, choices=STATUS_CHOICES, default=PENDING)

class Profile(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile')
    profile_pic = models.TextField(blank=True, null=True)
    ntrp_rating = models.PositiveSmallIntegerField(blank=True, null=True)
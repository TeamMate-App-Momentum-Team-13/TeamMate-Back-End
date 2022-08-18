from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

def restrict_amount(value):
        parent = GameSession.objects.get(id=value)
        if parent.match_type == 'Singles':
            if parent.guest.count() >= 3:
                raise ValidationError(f'Game Session already has maximal amount of Guest({3})')
        elif parent.match_type == 'Doubles':
            if parent.guest.count() >= 6:
                raise ValidationError(f'Game Session already has maximal amount of Guest ({6})')

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

    def __str__(self):
        return f"{self.pk} {self.host}, {self.match_type}, {self.session_type}"

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
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='guest', validators=(restrict_amount, ))
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
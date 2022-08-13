from pyexpat import model
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

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

class AddressModelMixin(BaseModel):
    address1 = models.CharField(max_length=250)
    address2 = models.CharField(max_length=250, blank=True, null=True)
    city = models.CharField(max_length=250)
    state = models.CharField(max_length=250)
    zipcode = models.CharField(max_length=5)

    def __str__(self):
        return f"{self.address1}, {self.city}, {self.state}, {self.zipcode}"

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
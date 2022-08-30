from django.contrib import admin
from .models import User, GameSession, Court, CourtAddress, UserAddress, Guest, Profile, AddressModelMixin, NotificationGameSession, Survey, SurveyResponse, RankUpdate
# Register your models here.

admin.site.register(User)
admin.site.register(GameSession)
admin.site.register(Court)
admin.site.register(CourtAddress)
admin.site.register(UserAddress)
admin.site.register(Guest)
admin.site.register(Profile)
admin.site.register(AddressModelMixin)
admin.site.register(NotificationGameSession)
admin.site.register(Survey)
admin.site.register(SurveyResponse)
admin.site.register(RankUpdate)

from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from api import views as api_views

router = routers.DefaultRouter()
router.register(r'guest', api_views.GuestViewSet, basename="guest")

urlpatterns = [
    path('session/<int:pk>/', include(router.urls)),
    path('admin/', admin.site.urls),
    path('auth/', include('rest_framework.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    # path('<str:username>', api_views.UserDetail.as_view(), name='profile'),
    path('profile', api_views.ListCreateUpdateProfile.as_view(), name='profile'),
    path('session', api_views.ListCreateGameSession.as_view(), name='game-session-list'),
    path('session/<int:pk>', api_views.RetrieveUpdateDestroyGameSession.as_view(), name='game-session-detail'),
]

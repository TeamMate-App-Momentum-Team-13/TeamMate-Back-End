"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from api import views as api_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('rest_framework.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('session', api_views.ListCreateGameSession.as_view(), name='game-session-list'),
    path('session/<int:pk>', api_views.RetrieveUpdateDestroyGameSession.as_view(), name='game-session-detail'),
    path('session/<int:pk>/guest', api_views.ListCreateGuest.as_view(), name='list_create_guest'),
    path('session/<int:pk>/guest/<int:guest_pk>', api_views.GameSessionGuest.as_view() ,name='game-session-guest-detail'),
]

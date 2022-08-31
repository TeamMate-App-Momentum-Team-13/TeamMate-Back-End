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
    path('<str:username>', api_views.UserDetail.as_view(), name='user-details'),
    path('<str:username>/games/', api_views.MyGamesList.as_view(), name='my-games'),
    path('profile/', api_views.ListCreateUpdateProfile.as_view(), name='profile'),
    path('session/', api_views.ListCreateGameSession.as_view(), name='game-session-list'),
    path('session/<int:pk>', api_views.RetrieveUpdateDestroyGameSession.as_view(),
        name='game-session-detail'),
    path('session/<int:session_pk>/survey/', api_views.ListCreateSurvey.as_view(),
        name='list-create-survey'),
    path('session/<int:session_pk>/survey/response/', api_views.CreateSurveyResponse.as_view(),
        name='list-create-survey-response'),
    path('court/', api_views.ListCreateCourt.as_view(), name='court'),
    path('court/<int:pk>/address/', api_views.ListCreateCourtAddress.as_view(),
        name='court-address'),
    path('notification/check/', api_views.CheckNotificationGameSession.as_view(),
        name='notification-check'),
    path('notification/count/', api_views.CountNotificationGameSession.as_view(),
        name='notification-count'),
    path('notification/all/', api_views.AllNotificationGameSession.as_view(),
        name='notification-all'),
]

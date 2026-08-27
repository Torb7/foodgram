from django.urls import path, include

from api import views

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
]

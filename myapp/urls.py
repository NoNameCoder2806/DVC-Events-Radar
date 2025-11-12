from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name='home'),
    path("calendar/", views.calendar, name='calendar'),
    path("map/", views.map, name="map"),
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
]
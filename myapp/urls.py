from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("", views.home, name='home'),
    path('calendar/', views.calendar_view, name='calendar'),  # use calendar_view
    path("map/", views.map, name="map"),
    path("login/", views.app_login, name="login"),
    path("logout/", views.app_logout, name="logout"),
    path("register/", views.register, name="register"),
    path("event_detail/<int:event_id>/", views.event_detail, name="event_detail"),
    path('favorite/<int:event_id>/', views.mark_favorite, name='mark_favorite'),
    path("add_event/", views.add_event, name="add_event"),
    path("manage-events/", views.manage_events, name="manage_events"),
    path("manage-events/edit/<int:event_id>/", views.edit_event, name="edit_event"),
    path("manage-events/delete/<int:event_id>/", views.delete_event, name="delete_event"),
    path("manage-users/", views.manage_users, name="manage_users"),
]
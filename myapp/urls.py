from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static

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
    path("manage-users/change-role/<int:user_id>/", views.change_user_role, name="change_user_role"),
    path("manage-users/delete/<int:user_id>/", views.delete_user, name="delete_user"),
    path("profile/", views.user_profile, name="user_profile")
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.apps import AppConfig
from django.db.models.signals import post_migrate
import os

class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

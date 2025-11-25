from django.db import models

class Users(models.Model):
    first_name = models.CharField(max_length=50, default=None, blank=True, null=True)
    last_name = models.CharField(max_length=50, default=None, blank=True, null=True)
    password = models.CharField(max_length=256)
    email = models.CharField(max_length=100)
    DVC_ID = models.CharField(max_length=10,default=None, blank=True, null=True)
    role = models.CharField(max_length=30)

class Events(models.Model): 
    author_ID = models.IntegerField()
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=10000)
    date = models.CharField(max_length=100)
    days_of_week = models.CharField(max_length=30)
    start_time = models.CharField(max_length=100)
    end_time = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    campus = models.CharField(max_length=100)
    event_type = models.CharField(max_length=100)
    image_url = models.URLField(default=None, blank=True, null=True)
    
class Favorites(models.Model):
    event_ID = models.IntegerField()
    user_ID = models.IntegerField()
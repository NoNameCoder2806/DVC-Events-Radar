from django.db import models

class User(models.Model):
    name = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    DVC_ID = models.IntegerField()
    role = models.CharField(max_length=30)

class Event(models.Model): 
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
    
class Favorite(models.Model):
    event_ID = models.IntegerField()
    user_ID = models.IntegerField()
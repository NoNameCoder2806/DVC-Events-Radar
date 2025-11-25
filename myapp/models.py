from django.db import models
from django.contrib.auth.models import User

class Users(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    DVC_ID = models.CharField(max_length=10,default=None, blank=True, null=True)
    role = models.CharField(max_length=30)
    
    def __str__(self):
        return self.user.username

class Events(models.Model): 
    author_ID = models.ForeignKey(Users, on_delete=models.CASCADE)
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
    
    def __str__(self):
        return self.name     
    
class Favorites(models.Model):
    event_ID = models.ForeignKey(Events, on_delete=models.CASCADE)
    user_ID = models.ForeignKey(Users, on_delete=models.CASCADE)
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Users(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    DVC_ID = models.CharField(max_length=10,default=None, blank=True, null=True)
    role = models.CharField(max_length=30)
    
    def __str__(self):
        return self.user.username
        
    class Meta:        
        verbose_name = "User"
        verbose_name_plural = "Users"

class Events(models.Model): 
    author_ID = models.ForeignKey(Users, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=10000)
    date = models.DateField(default=timezone.now)
    start_time = models.CharField(max_length=100)
    end_time = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    campus = models.CharField(max_length=100)
    event_type = models.CharField(max_length=100)
    image_url = models.URLField(default=None, blank=True, null=True)
    
    def __str__(self):
        return self.name     
    
    class Meta:        
        verbose_name = "Event"
        verbose_name_plural = "Events"
    
class Favorites(models.Model):
    event_ID = models.ForeignKey(Events, on_delete=models.CASCADE)
    user_ID = models.ForeignKey(Users, on_delete=models.CASCADE)
    
    class Meta:        
        verbose_name = "Favorite"
        verbose_name_plural = "Favorites"
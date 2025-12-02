from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import os

def user_avatar_path(instance, filename):
    ext = filename.split('.')[-1]
    # instance.user.id will always exist here because user is saved
    return os.path.join('avatars', str(instance.user.id), f'avatar.{ext}')

class Users(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    DVC_ID = models.CharField(max_length=10,default=None, blank=True, null=True)
    role = models.CharField(max_length=30)
    avatar_url = models.ImageField(
        upload_to=user_avatar_path,  # new path function
        blank=True,
        null=True
    )
    
    def __str__(self):
        return self.user.username
    
def event_image_path(instance, filename):
    # instance.id won't exist until saved for the first time, so we handle that
    ext = filename.split('.')[-1]
    if instance.id:
        filename = f'{instance.id}.{ext}'
    else:
        filename = f'temp.{ext}'  # temporary name, will rename after save
    return os.path.join('events', str(instance.id or 'temp'), filename)

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
    image = models.ImageField(
        upload_to=event_image_path,  # folder inside MEDIA_ROOT
        default="events/default.jpg",  # optional default image
        blank=True,
        null=True
    )

    def delete(self, *args, **kwargs):
        # Delete the image file if it exists
        if self.image and os.path.isfile(self.image.path):
            os.remove(self.image.path)
        super().delete(*args, **kwargs)
    
    def __str__(self):
        return self.name     
    
class Favorites(models.Model):
    event_ID = models.ForeignKey(Events, on_delete=models.CASCADE)
    user_ID = models.ForeignKey(Users, on_delete=models.CASCADE)
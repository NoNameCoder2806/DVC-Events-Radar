from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q 
from django.utils import timezone
from datetime import datetime
from django.conf import settings
import os
import re

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
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        
def event_image_path(instance, filename):
    # instance.id won't exist until saved for the first time, so we handle that
    ext = filename.split('.')[-1]
    if instance.id:
        filename = f'{instance.id}.{ext}'
    else:
        filename = f'temp.{ext}'  # temporary name, will rename after save
    return os.path.join('events', str(instance.id or 'temp'), filename)

class EventSearch(models.Manager):
    # If you surround your query with " " , it searches events containing the exact phrase 
    # If you search without quotemarks, it earches posts that contains all the words in the query
    # Ex) If you search `Coffee break` events like `break with coffee` appear 
    # Not Case sensitive
    def search(self, query):
        phrases = re.findall(r'"(.*?)"', query)
        remaining = re.sub(r'"(.*?)"', '', query)
        words = [w for w in remaining.split() if w] 
        
        q_objects = Q()
        
        # Exact phrase search
        for phrase in phrases:
            q_objects |= Q(name__icontains=phrase) | Q(description__icontains=phrase)  | Q(location__icontains=phrase)
        # Default search
        for word in words:
            q_objects &= Q(name__icontains=word) | Q(description__icontains=word) | Q(location__icontains=word)
            
        return self.get_queryset().filter(q_objects).distinct()

class Events(models.Model): 
    EVENT_TYPES = [('Sports', 'Sports'), ('Clubs', 'Clubs'),('Career & Academic', 'Career & Academic'), ('Free Food', 'Free Food'), ('General', 'General')]    
    CAMPUS_CHOICES = [('Pleasant Hill', 'Pleasant Hill'),('San Ramon', 'San Ramon'),('Virtual', 'Virtual')]
    PH_BUILDINGS = [
        ('A', 'Art Complex'), ('AB', 'Administration'), ('BC', 'Book Center'), ('BWL', 'Business & World Language'), 
        ('ECN', 'Early Childhood Education North'), ('ECS', 'Early Childhood Education South'), ('ET', 'Engineering Technology'),
        ('ETT', 'Engineering Technology Temporary'), ('FO', 'Faculty Offices'), ('H', 'Humanities'), ('HFO', 'Health Faculty Offices'),
        ('HRT', 'Horticulture'), ('HSF', 'Hospitality Studies & Food Court'), ('KIN', 'Kinesiology'), ('L', 'Library'), ('LA', 'Liberal Arts'),
        ('LC', 'Learning Center'), ('LCA', 'Learning Communities Annex'), ('LS', 'Life Sciences'), ('M', 'Music'), ('MA', 'Mathematics'),
        ('PAO', 'Performing Arts Office'), ('PL', 'Planetarium'), ('POL', 'Police Services'), ('PS', 'Physical Science'),
        ('SSC', 'Student Services Center'), ('ST', 'Science and Technology Center'), ('SU', 'Student Union'), ('W', 'Warehouse'),
        ('WLC', 'West Library Classrooms'), ('AQ', 'Aquatics'), ('FBO', 'Football Office'), ('FH', 'Field House'), ('FTX', 'Fitness & Exercise'),
        ('GYM', 'Gym'), ('PB', 'Press Box'), ('AR', 'Arena Theater'), ('PAC', 'Performing Arts Center'),
    ]
    SR_BUILDINGS = [
        ('SR-WEST', 'West Building'), ('SR-EAST', 'East Building'), ('SR-LC', 'Learning Commons'), ('SR-LIB', 'Library'), ('SR-MP', 'Mechanical Plant'),
    ]
    BUILDING_CODES = (
        PH_BUILDINGS +
        SR_BUILDINGS +
        [('VR', 'Virtual Event')]
    )
    BUILDING_COORDINATES = {
        # Pleasant Hill (placeholder coords — we will fill real ones)
        "A": (37.968800, -122.062500),
        "AB": (37.969200, -122.061900),
        # ... continue for all PH buildings ...

        # San Ramon
        "SR-WEST": (37.774500, -121.953900),
        "SR-EAST": (37.774200, -121.953300),
        "SR-LC": (37.774700, -121.953000),
        "SR-LIB": (37.774600, -121.953100),
        "SR-MP": (37.775100, -121.953400),

        # Virtual
        "VR": None,
    }
    
    author_ID = models.ForeignKey(Users, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=10000)
    date = models.DateField(default=timezone.now)
    start_time = models.CharField(max_length=100)
    end_time = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True, null=True)
    campus = models.CharField(max_length=100, choices=CAMPUS_CHOICES)
    building_code = models.CharField(
        max_length=10,
        choices=BUILDING_CODES,
        blank=True,
        null=True,
        help_text="Select a building for on-campus events (VR for Virtual)."
    )
    event_type = models.CharField(max_length=100, choices=EVENT_TYPES)
    image = models.ImageField(
        upload_to=event_image_path,  # folder inside MEDIA_ROOT
        default="events/default.jpg",  # optional default image
        blank=True,
        null=True
    )
    
    objects = EventSearch()
    
    @property 
    def start_time_obj(self):
        try:
            return datetime.strptime(self.start_time.strip(), "%I:%M %p").time()
        except Exception:
            return None
    
    @property
    def end_time_obj(self):
        try:    
            return datetime.strptime(self.end_time.strip(), "%I:%M %p").time()
        except Exception:
            return None
            
    @property
    def image_or_default(self):
        try: 
            if self.image and os.path.isfile(self.image.path):
                return self.image.url
        except ValueError:
            pass
        return settings.MEDIA_URL + '/default.jpg'

    def delete(self, *args, **kwargs):
        # Delete the image file if it exists
        if self.image and os.path.isfile(self.image.path):
            os.remove(self.image.path)
        super().delete(*args, **kwargs)
    
    def __str__(self):
        return self.name

    @property
    def coordinates(self):
        return self.BUILDING_COORDINATES.get(self.building_code)         
        
    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        
    
    
class Favorites(models.Model):
    event_ID = models.ForeignKey(Events, on_delete=models.CASCADE)
    user_ID = models.ForeignKey(Users, on_delete=models.CASCADE)    
    
    class Meta:
        verbose_name = "Favorite"
        verbose_name_plural = "Favorites"
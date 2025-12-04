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
        [('VR', 'Virtual')]
    )
    BUILDING_COORDINATES = {
        # Pleasant Hill
        "A":   (37.96970240752903, -122.06857796884242),    # Art Complex
        "AB":  (37.96857499999999, -122.07312000000002),    # Administration Building
        "BC":  (37.96856863253504, -122.07127399999990),    # Book Center
        "BWL": (37.96950801850639, -122.07254094329996),    # Business & World Language
        "ECN": (37.96950142338789, -122.07299000000006),    # Early Childhood Education North
        "ECS": (37.96924697952306, -122.07296887432731),    # Early Childhood Education South
        "ET":  (37.96713388859415, -122.07123174105897),    # Engineering Technology
        "ETT": (37.96974361261291, -122.07113046399996),    # Engineering Technology Temporary
        "FO":  (37.96879881982005, -122.07261652700004),    # Faculty Offices
        "H":   (37.96948677554036, -122.07200269484486),    # Humanities
        "HFO": (37.96833986589479, -122.06922201553477),    # Health Faculty Offices
        "HRT": (37.96958995495550, -122.06798926353783),    # Horticulture
        "HSF": (37.96928864063594, -122.07121569045374),    # Hospitality Studies & Food Court
        "KIN": (37.96896264231282, -122.06812093067082),    # Kinesiology
        "L":   (37.96762096728274, -122.07242808476262),    # Library
        "LA":  (37.96880663435614, -122.07200613616711),    # Liberal Arts
        "LC":  (37.96827350000034, -122.07256299999995),    # Learning Center
        "LCA": (37.96830550000005, -122.07213943000002),    # Learning Communities Annex
        "LS":  (37.96738624666404, -122.07384145200661),    # Life Sciences
        "M":   (37.96801628299996, -122.06980966686377),    # Music
        "MA":  (37.96810862319616, -122.07115637248642),    # Mathematics
        "PAO": (37.96967800000055, -122.06986905000002),    # Performing Arts Office
        "PL":  (37.96782047153108, -122.07343608834377),    # Planetarium
        "POL": (37.96741900000001, -122.07056399999999),    # Police Services
        "PS":  (37.96744647155537, -122.07314736936552),    # Physical Science
        "SSC": (37.96891523533683, -122.07135448895589),    # Student Services Center
        "ST":  (37.96828411387047, -122.07387406503243),    # Science and Technology Center
        "SU":  (37.96896853239968, -122.07012823035115),    # Student Union
        "W":   (37.97001309046124, -122.06760005702555),    # Warehouse
        "WLC": (37.96753708154396, -122.07283561241345),    # West Library Classrooms
        "AQ":  (37.96871113961416, -122.06849828158062),    # Aquatics
        "FBO": (37.96752575809212, -122.06838736122332),    # Football Office
        "FH":  (37.96799047153086, -122.06886883834257),    # Field House
        "FTX": (37.96931903111456, -122.06887875271894),    # Fitness & Exercise
        "GYM": (37.96829172994966, -122.06875502606068),    # Gym
        "PB":  (37.96701950000009, -122.06959786249988),    # Press Box
        "AR":  (37.96922400000022, -122.06971000000016),    # Arena Theater
        "PAC": (37.96944105691815, -122.06996933834286),    # Performing Arts Center

        # San Ramon
        "SR-WEST": (37.75496847390289, -121.91041226441861),      # San Ramon West Building
        "SR-EAST": (37.75473372697604, -121.90974463229286),      # San Ramon East Building
        "SR-LC":   (37.75485993400142, -121.91081279723862),      # San Ramon Learning Commons
        "SR-LIB":  (37.75466158409603, -121.91027992055231),      # San Ramon Library
        "SR-MP":   (37.75498194513493, -121.91125603403335),      # San Ramon Mechanical Plant

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
    # building_code = models.CharField(
    #     max_length=10,
    #     choices=BUILDING_CODES,
    #     default = "VR",
    #     blank=True,
    #     null=True,
    #     help_text="Select a building for on-campus events (VR for Virtual)."
    # )
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
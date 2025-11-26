# myapp/apps.py
from django.apps import AppConfig
from django.db.models.signals import post_migrate

def populate_events(sender, **kwargs):
    from django.contrib.auth.models import User
    from .models import Users, Events
    
    # Check if events already exist
    if Events.objects.exists():
        return

    # Ensure at least one Users instance exists
    if not Users.objects.exists():
        # Create a default Django user
        user_obj = User.objects.create_user(username='admin', password='password')
        Users.objects.create(user=user_obj, DVC_ID='0001', role='admin')
    
    # Get an author for events
    author = Users.objects.first()

    # Create 10 sample events
    for i in range(1, 11):
        Events.objects.create(
            author_ID=author,
            name=f'Sample Event {i}',
            description=f'This is the description for Sample Event {i}.',
            date='2025-12-01',
            days_of_week='Mon,Wed,Fri',
            start_time='10:00 AM',
            end_time='12:00 PM',
            location=f'Building {i}',
            campus='Main Campus',
            event_type='Workshop',
            image_url=''
        )

class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'
    def ready(self):
        post_migrate.connect(populate_events, sender=self)
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from myapp.models import Users, Events
from django.utils import timezone

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Create users
        if not Users.objects.exists():
            default_users = [
                {"username": "andrew@insite.4cd.edu", "DVC_ID": "0000001", "role": "admin"},
                {"username": "frank@insite.4cd.edu", "DVC_ID": "0000002", "role": "admin"},
                {"username": "heidi@insite.4cd.edu", "DVC_ID": "0000003", "role": "admin"},
                {"username": "hoang@insite.4cd.edu", "DVC_ID": "0000004", "role": "admin"},
                {"username": "kayla@insite.4cd.edu", "DVC_ID": "0000005", "role": "admin"},
                {"username": "seokyoung@insite.4cd.edu", "DVC_ID": "0000006", "role": "admin"},
                {"username": "dvc_user@insite.4cd.edu", "DVC_ID": "0000007", "role": "user"}
            ]

        for u in default_users:
            user_obj = User.objects.create_user(username=u["username"], password="password")
            Users.objects.create(user=user_obj, DVC_ID=u["DVC_ID"], role=u["role"])
            
        if not User.objects.filter(username="dvc_default@insite.4cd.edu").exists():
            superuser = User.objects.create_superuser(
                username = "dvc_default@insite.4cd.edu", 
                email = "dvc_default@insite.4cd.edu", 
                password = "password"
            )
            Users.objects.create(user=superuser, DVC_ID="00000000", role = "superuser")
            
        print("Created 8 default users.")

        # Check if Events already exist
        if Events.objects.exists():
            print("Events already exist. Skipping event creation.")
        else:
            author = Users.objects.first()  # default DVC user as author

        event_data = [
            # Nov 25
            {
                "name": "Academic Senate Meeting",
                "date": "2025-11-25",
                "start_time": "2:30 PM",
                "end_time": "4:00 PM",
                "location": "Virtual",
                "campus": "Pleasant Hill",
            },

            # Nov 28
            {
                "name": "All in the Timing",
                "date": "2025-11-28",
                "start_time": "7:30 PM",
                "end_time": "9:30 PM",
                "campus": "Pleasant Hill",
            },

            # Nov 29
            {
                "name": "DVC Horticulture Plant Sale",
                "date": "2025-11-29",
                "start_time": "10:00 AM",
                "end_time": "2:00 PM",
                "campus": "Pleasant Hill",
            },
            {
                "name": "All in the Timing",
                "date": "2025-11-29",
                "start_time": "7:30 PM",
                "end_time": "9:30 PM",
                "campus": "Pleasant Hill",
            },

            # Nov 30
            {
                "name": "All in the Timing",
                "date": "2025-11-30",
                "start_time": "2:00 PM",
                "end_time": "4:00 PM",
                "campus": "Pleasant Hill",
            },

            # Dec 01
            {
                "name": "Distance Education & Digital Equity Committee",
                "date": "2025-12-01",
                "start_time": "12:30 PM",
                "end_time": "2:00 PM",        
                "location": "Virtual",
                "campus": "Pleasant Hill",
            },
            {
                "name": "Curriculum Committee Meeting",
                "date": "2025-12-01",
                "start_time": "2:30 PM",
                "end_time": "4:30 PM",        
                "location": "Virtual",
                "campus": "Pleasant Hill",
            },

            # Dec 02
            {
                "name": "Art Department Holiday Art Sale",
                "date": "2025-12-02",
                "start_time": "9:00 AM",
                "end_time": "3:00 PM",
                "campus": "Pleasant Hill",
            },
            {
                "name": "Business Beyond the Classroom - Scholarships & DVC Alumni Association",
                "date": "2025-12-02",
                "start_time": "1:00 PM",
                "end_time": "3:00 PM",
                "location": "Virtual",
                "campus": "Pleasant Hill",
            },
            {
                "name": "Academic Senate Meeting",
                "date": "2025-12-02",
                "start_time": "2:30 PM",
                "end_time": "4:00 PM",
                "location": "Virtual",
                "campus": "Pleasant Hill",
            },
        ]

        for ev in event_data:
            Events.objects.create(
                author_ID=author,
                name=ev["name"],
                description=f"This is the event: {ev['name']}",
                date=ev["date"],
                start_time=ev["start_time"],
                end_time=ev["end_time"],
                location=ev.get("location"),
                campus="Pleasant Hill",
                event_type="General"
            )
        print("Created sample events.")

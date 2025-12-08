from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.conf import settings
import os
import json


class MyappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "myapp"

    def ready(self):
        post_migrate.connect(populate_default_data, sender=self)


def populate_default_data(sender, **kwargs):
    """
    This function automatically seeds:
    - Default Users
    - Events from JSON file
    whenever migrations run.
    """

    from myapp.models import Users, Events  # Import inside function to avoid AppRegistry errors

    print("[populate_default_data] Running...")

    # -------- USERS (DEFAULT ADMIN) --------
    if not Users.objects.exists():
        user = Users.objects.create(
            username="admin",
            email="admin@example.com",
            password="admin",
            firstName="Admin",
            lastName="User",
        )
        print("[populate_default_data] Created default admin user.")
    else:
        print("Users already exist. Skipping user creation.")

    author = Users.objects.first()

    # -------- EVENTS (SYNC FROM JSON) --------
    json_path = os.path.join(settings.BASE_DIR, "myapp", "data", "dvc_events.json")

    if not os.path.exists(json_path):
        print(f"[populate_default_data] JSON file not found: {json_path}")
        return

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            event_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[populate_default_data] JSON decode error: {e}")
        return

    created_count = 0
    updated_count = 0

    for ev in event_data:

        # each event is uniquely identified by ALL of these fields
        lookup = {
            "name": ev.get("name", ""),
            "date": ev.get("date", ""),
            "start_time": ev.get("start_time", ""),
            "end_time": ev.get("end_time", ""),
            "location": ev.get("location", ""),
            "campus": ev.get("campus", ""),
        }

        defaults = {
            "author_ID": author,
            "description": ev.get("description", ""),
            "days_of_week": "",
            "event_type": ev.get("event_type") or "General",
        }

        event, created = Events.objects.update_or_create(
            **lookup,
            defaults=defaults,
        )

        # Assign image if provided
        image_filename = ev.get("image_filename")
        if image_filename:
            event.image.name = os.path.join("events", image_filename)
            event.save()

        if created:
            created_count += 1
        else:
            updated_count += 1

    print(f"[populate_default_data] Synced events. Created: {created_count}, Updated: {updated_count}")

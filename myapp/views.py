from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from .models import Users, Events, Favorites
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages

def get_data():    
    users_data = Users.objects.all()
    events_data = Events.objects.all()
    favorites_data = Favorites.objects.all()
    data = {
        'users_data':users_data,
        'events_data':events_data, 
        'favorites_data':favorites_data
    }
    return data

def home(request):
    today = timezone.now().date()
    events_data = Events.objects.filter(date__gte=today)

    # Group events by date
    events_by_date = {}
    for event in events_data:
        events_by_date.setdefault(event.date, []).append(event)

    # Sort events within each date by start_time
    for date, events in events_by_date.items():
        def parse_time(e):
            try:
                return datetime.strptime(e.start_time.strip(), "%I:%M %p")
            except ValueError:
                # fallback if someone entered 24-hour time
                return datetime.strptime(e.start_time.strip(), "%H:%M")
        events.sort(key=parse_time)

    # Flatten sorted events
    sorted_events = []
    for date in sorted(events_by_date.keys()):
        sorted_events.extend(events_by_date[date])

    # Assign display times
    for event in sorted_events:
        event.start_time_display = event.start_time
        event.end_time_display = event.end_time

    # User favorites
    user_favorites = []
    user_role = None
    if request.user.is_authenticated:
        try:
            user_obj = Users.objects.get(user=request.user)
            user_favorites = list(Favorites.objects.filter(user_ID=user_obj).values_list('event_ID__id', flat=True))
            user_role = user_obj.role
        except Users.DoesNotExist:
            pass

    return render(request, 'home.html', {
        'events_data': sorted_events,
        'user_favorites': user_favorites,
        'user_id': request.user.id if request.user.is_authenticated else None,
        'user_name': request.user.username if request.user.is_authenticated else None,
        'user_role': user_role,
    })

def calendar_view(request):
    today = datetime.datetime.today()
    events_per_day = {}  # key = day of month, value = count of favorite events

    if request.user.is_authenticated:
        try:
            user_obj = Users.objects.get(user=request.user)
            favorite_events = Favorites.objects.filter(user_ID=user_obj).select_related('event_ID')
            for fav in favorite_events:
                try:
                    event_date = datetime.datetime.strptime(fav.event_ID.date.strip(), "%Y-%m-%d")
                    day_key = event_date.strftime("%Y-%m-%d")  # YYYY-MM-DD
                    events_per_day[day_key] = events_per_day.get(day_key, 0) + 1
                except Exception as e:
                    print(f"Skipping invalid date {fav.event_ID.date}: {e}")
        except Users.DoesNotExist:
            pass

    context = {
        "events_per_day": events_per_day,  # now only includes “interested” events
    }
    return render(request, "calendar.html", context)

def map(request):
    return render(request, 'map.html')

def app_login(request):
    if request.method == "POST":
        email = request.POST.get("email").lower()
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")  # successful login
        else:
            # if password is wrong
            # invalid login
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    else:
        return render(request, 'login.html')
    
def app_logout(request):
    logout(request) # clears all session data
    return redirect("home")

def register(request):
    if request.method == "GET":
        return render(request, 'register.html')

    elif request.method == "POST":
        user_default = User.objects.create_user(
            username = request.POST.get("email").lower(), 
            first_name = request.POST.get("first_name"),
            last_name = request.POST.get("last_name"),
            email = request.POST.get("email").lower(),
            password = request.POST.get("password"),
        )
        user_register = Users(
            user = user_default,             
            DVC_ID = request.POST.get("DVC_ID"),
            role = 'user'           
        )
        user_register.save()
        return redirect("login")

def event_detail(request, event_id):
    event = get_object_or_404(Events, id=event_id)

    # Get user's favorite event IDs
    user_favorites = []
    if request.user.is_authenticated:
        try:
            user_obj = Users.objects.get(user=request.user)
            user_favorites = list(
                Favorites.objects.filter(user_ID=user_obj)
                .values_list('event_ID__id', flat=True)
            )
        except Users.DoesNotExist:
            user_favorites = []

    return render(request, "event_detail.html", {
        "event": event,
        "user_favorites": user_favorites,
    })

def mark_favorite(request, event_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'User not logged in'})

    # Get the event instance
    event_obj = get_object_or_404(Events, id=event_id)

    # Get the corresponding Users instance for the logged-in user
    try:
        user_obj = Users.objects.get(user=request.user)
    except Users.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Users profile not found'})

    # Check if favorite exists
    favorite = Favorites.objects.filter(user_ID=user_obj, event_ID=event_obj).first()

    if favorite:
        favorite.delete()
        return JsonResponse({'status': 'removed'})
    else:
        Favorites.objects.create(user_ID=user_obj, event_ID=event_obj)
        return JsonResponse({'status': 'added'})
    
def add_event(request):
    # Only logged-in users
    if not request.user.is_authenticated:
        return redirect('login')

    # Get user profile
    try:
        user_profile = Users.objects.get(user=request.user)
    except Users.DoesNotExist:
        return HttpResponseForbidden("User profile not found")

    # Only admins or superusers can add events
    if user_profile.role not in ["admin", "superuser"]:
        return HttpResponseForbidden("You do not have permission to add events.")

    # Hour and minute dropdown options
    hours = list(range(1, 13))  # 1-12
    minutes = ["00", "15", "30", "45"]
    previous = request.POST if request.method == 'POST' else None

    if request.method == 'POST':
        # Build start and end times
        try:
            start_hour = int(request.POST.get('start_hour'))
            start_minute = int(request.POST.get('start_minute'))
            start_period = request.POST.get('start_period')
            start_time_str = f"{start_hour}:{start_minute:02d} {start_period}"

            end_hour = int(request.POST.get('end_hour'))
            end_minute = int(request.POST.get('end_minute'))
            end_period = request.POST.get('end_period')
            end_time_str = f"{end_hour}:{end_minute:02d} {end_period}"

            # Validate time order
            start_obj = datetime.strptime(start_time_str, "%I:%M %p")
            end_obj = datetime.strptime(end_time_str, "%I:%M %p")
            if start_obj >= end_obj:
                messages.error(request, "Start time must be before end time.")
                raise ValueError("Invalid time order")

            # Parse date and day of week
            event_date_str = request.POST.get('date')
            event_date_obj = datetime.strptime(event_date_str, "%Y-%m-%d").date()
            day_of_week = event_date_obj.strftime("%A")

            # Save event
            Events.objects.create(
                author_ID=user_profile,
                name=request.POST.get('name'),
                description=request.POST.get('description'),
                date=event_date_str,
                days_of_week=day_of_week,
                start_time=start_time_str,
                end_time=end_time_str,
                location=request.POST.get('building'),  # consistently using "building"
                campus=request.POST.get('campus'),
                event_type=request.POST.get('event_type'),
                image_url=request.FILES.get('image') if 'image' in request.FILES else None
            )
            messages.success(request, "Event added successfully!")
            return redirect('home')

        except Exception as e:
            # Re-render form with previous values
            return render(request, 'add_event.html', {
                'hours': hours,
                'minutes': minutes,
                'previous': previous
            })

    previous = request.POST if request.method == 'POST' else {}
    return render(request, 'add_event.html', {
        'hours': hours,
        'minutes': minutes,
        'previous': previous,
    })

@user_passes_test(lambda u: u.is_authenticated and hasattr(u, "users") and u.users.role in ["admin", "superuser"])
def manage_events(request):
    all_events = list(Events.objects.all())

    # Sort events by date, then by start_time (handle 12-hour and 24-hour formats)
    def sort_key(e):
        try:
            t = datetime.strptime(e.start_time.strip(), "%I:%M %p")
        except ValueError:
            t = datetime.strptime(e.start_time.strip(), "%H:%M")
        return (e.date, t)

    all_events.sort(key=sort_key)

    return render(request, "manage_events.html", {"all_events": all_events})

def delete_event(request, event_id):
    event = get_object_or_404(Events, id=event_id)

    if request.method == "POST":
        event.delete()
        messages.success(request, "Event deleted successfully.")
        return redirect("manage_events")

    return render(request, "confirm_delete.html", {"event": event})

def edit_event(request, event_id):
    event = get_object_or_404(Events, id=event_id)
    return render(request, "edit_event.html", {"event": event})

@user_passes_test(lambda u: u.is_authenticated and hasattr(u, "users") and u.users.role == "superuser")
def manage_users(request):
    all_users = Users.objects.all()
    return render(request, "manage_users.html", {"all_users": all_users})
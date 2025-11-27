from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from .models import Users, Events, Favorites
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import datetime

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
    # All events
    events_data = Events.objects.all()

    # User favorites
    user_favorites = []
    if request.user.is_authenticated:
        try:
            user_obj = Users.objects.get(user=request.user)
            user_favorites = list(Favorites.objects.filter(user_ID=user_obj).values_list('event_ID__id', flat=True))
        except Users.DoesNotExist:
            user_favorites = []

    # Pass context to template
    return render(request, 'home.html', {
        'events_data': events_data,
        'user_favorites': user_favorites,
        'user_id': request.user.id if request.user.is_authenticated else None,
        'user_name': request.user.username if request.user.is_authenticated else None,
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
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        user_profile = Users.objects.get(user=request.user)
    except Users.DoesNotExist:
        return HttpResponseForbidden("Users profile not found")

    if user_profile.role not in ["admin", "superuser"]:
        return HttpResponseForbidden("You do not have permission to add events.")

    if request.method == 'POST':
        start_hour = int(request.POST.get('start_hour'))
        start_minute = request.POST.get('start_minute')
        start_period = request.POST.get('start_period')
        if start_period == "PM" and start_hour != 12:
            start_hour += 12
        elif start_period == "AM" and start_hour == 12:
            start_hour = 0
        start_time = f"{start_hour:02d}:{start_minute}"

        end_hour = int(request.POST.get('end_hour'))
        end_minute = request.POST.get('end_minute')
        end_period = request.POST.get('end_period')
        if end_period == "PM" and end_hour != 12:
            end_hour += 12
        elif end_period == "AM" and end_hour == 12:
            end_hour = 0
        end_time = f"{end_hour:02d}:{end_minute}"

        Events.objects.create(
            author_ID=user_profile,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            date=request.POST.get('date'),
            days_of_week=','.join(request.POST.getlist('days_of_week')),
            start_time=start_time,
            end_time=end_time,
            location=request.POST.get('location'),
            campus=request.POST.get('location'),
            event_type=request.POST.get('event_type'),
            image_url=request.POST.get('image_url') or None
        )
        return redirect('home')

    # Generate hour/minute/period options
    hours = list(range(1, 13))  # 1 to 12
    minutes = ["00", "15", "30", "45"]

    return render(request, 'add_event.html', {
        'hours': hours,
        'minutes': minutes
    })

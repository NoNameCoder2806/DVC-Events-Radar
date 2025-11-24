from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Users, Events, Favorites
from datetime import datetime

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
    data = get_data()
    user_id = request.session.get('user_id')
    data['user_id'] = user_id
    data['user_name'] = request.session.get('user_name')

    if user_id:
        data['user_favorites'] = list(
            Favorites.objects.filter(user_ID=user_id).values_list('event_ID', flat=True)
        )
    else:
        data['user_favorites'] = []

    return render(request, 'home.html', data)

def calendar_view(request):
    user_id = request.session.get('user_id')
    favorite_days = []

    if user_id:
        # Get favorite event IDs for this user
        favorite_event_ids = Favorites.objects.filter(user_ID=user_id).values_list('event_ID', flat=True)
        favorite_events = Events.objects.filter(id__in=favorite_event_ids)

        # Extract day numbers for events in the current month/year
        today = datetime.today()
        for event in favorite_events:
            # Convert string to datetime
            try:
                event_date = datetime.strptime(event.date, "%Y-%m-%d")  # adjust format if needed
                if event_date.month == today.month and event_date.year == today.year:
                    favorite_days.append(event_date.day)
            except Exception as e:
                print(f"Skipping invalid date {event.date}: {e}")

    context = {
        "user_favorites_days": favorite_days
    }
    return render(request, "calendar.html", context)

def map(request):
    return render(request, 'map.html')

def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            user = Users.objects.get(email=email, password=password)
            # Store session info
            request.session['user_id'] = user.id
            request.session['user_name'] = f"{user.first_name} {user.last_name}"
            return redirect("home")  # successful login
        except Users.DoesNotExist:
            # invalid login
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    else:
        return render(request, 'login.html')
    
def logout(request):
    request.session.flush()  # clears all session data
    return redirect("home")

def register(request):
    if request.method == "GET":
        return render(request, 'register.html')

    elif request.method == "POST":
        user_register = Users(
            first_name = request.POST.get("first_name"),
            last_name = request.POST.get("last_name"),
            email = request.POST.get("email"),
            password = request.POST.get("password"),
            DVC_ID = request.POST.get("DVC_ID"),
            role = 'user'
        )
        user_register.save()
        return redirect("login")
    
def event_detail(request, event_id):
    event = get_object_or_404(Events, id=event_id)
    return render(request, "event_detail.html", {"event": event})

def mark_favorite(request, event_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'status': 'error', 'message': 'User not logged in'}, status=403)

    # Check if already favorited
    favorite_exists = Favorites.objects.filter(user_ID=user_id, event_ID=event_id).exists()
    if favorite_exists:
        # Optionally, unmark if already favorited
        Favorites.objects.filter(user_ID=user_id, event_ID=event_id).delete()
        return JsonResponse({'status': 'removed'})
    
    # Mark as favorite
    Favorites.objects.create(user_ID=user_id, event_ID=event_id)
    return JsonResponse({'status': 'added'})
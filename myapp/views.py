from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test

from django.utils import timezone
from django.utils.timezone import localtime
from datetime import datetime

from .models import Users, Events, Favorites
from .forms import EventForm

from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt, csrf_protect 
from django.conf import settings
import os
import json

from PIL import Image

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
    events_data = list(Events.objects.all())
    events_data.sort(key=lambda e: (e.date, e.start_time_obj or datetime.min.time()))

    user_role = None
    # User favorites
    user_favorites = []
    if request.user.is_authenticated:
        try:
            user_obj = Users.objects.get(user=request.user)
            user_favorites = list(Favorites.objects.filter(user_ID=user_obj).values_list('event_ID__id', flat=True))
            user_role = user_obj.role
        except Users.DoesNotExist:
            user_favorites = []

    # ===== PAGINATION =====
    paginator = Paginator(events_data, 10)  # 10 events per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'home.html', {
        'events_data': page_obj,
        'user_favorites': user_favorites,
        'user_id': request.user.id if request.user.is_authenticated else None,
        'user_name': request.user.username if request.user.is_authenticated else None,
        'user_role' : user_role, 
    })

def calendar_view(request):
    today = datetime.today()
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

    # if request.user.is_authenticated:
    #     try:
    #         user_obj = Users.objects.get(user=request.user)
    #         # Get only favorite events for this user
    #         favorite_events = Favorites.objects.filter(user_ID=user_obj).select_related('event_ID')
    #         for fav in favorite_events:
    #             try:
    #                 event_date = datetime.datetime.strptime(fav.event_ID.date.strip(), "%Y-%m-%d")
    #                 if event_date.month == today.month and event_date.year == today.year:
    #                     day = event_date.day
    #                     events_per_day[day] = events_per_day.get(day, 0) + 1
    #             except Exception as e:
    #                 print(f"Skipping invalid date {fav.event_ID.date}: {e}")
    #     except Users.DoesNotExist:
    #         pass

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

    user_profile = getattr(request.user, 'users', None) 
    if not user_profile or user_profile.role not in ["admin", "superuser"]:
        messages.error(request, "You do not have permission to add events.")
        return redirect('home')
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            new_event = form.save(commit=False)
            new_event.author_ID = user_profile
            new_event.save()
            messages.success(request, "Event added successfully.")
            return redirect('home')
        else:
            messages.error(request, "Please correct errors below.")
    else:
        form = EventForm()

    return render(request, 'event_form.html', {'form': form, 'page_title': 'Add Event', 'submit_text': 'Add Event'})

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
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated successfully.")
            return redirect('manage_events')
    else:
        form = EventForm(instance=event)
        
    return render(request, "event_form.html", {'event': event, 'form': form, 'page_title': 'Edit Event', 'submit_text': 'Update event'})

def manage_users(request):
    all_users = User.objects.all()
    return render(request, "manage_users.html", {"all_users": all_users})

@csrf_protect
def change_user_role(request, user_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Not logged in'})
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

    try:
        user = User.objects.get(id=user_id)
        profile = user.users
        try:
            data = json.loads(request.body)
            new_role = data.get('role')
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'})

        if new_role not in ['user', 'admin', 'superuser']:
            return JsonResponse({'status': 'error', 'message': 'Invalid role'})

        profile.role = new_role
        profile.save()
        return JsonResponse({'status': 'success'})

    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found'})

@csrf_exempt
def delete_user(request, user_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Not logged in'})

    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return JsonResponse({'status': 'success'})
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found'})
    
@login_required
def user_profile(request):
    user_obj = request.user
    profile_obj = user_obj.users

    if request.method == "POST":
        # Update first and last name
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        if first_name:
            user_obj.first_name = first_name
        if last_name:
            user_obj.last_name = last_name

        # Update avatar if uploaded
        if "avatar" in request.FILES:
            # Delete old avatar if it exists
            if profile_obj.avatar_url and os.path.isfile(profile_obj.avatar_url.path):
                os.remove(profile_obj.avatar_url.path)
            # Save new avatar
            profile_obj.avatar_url = request.FILES["avatar"]

        user_obj.save()
        profile_obj.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("user_profile")

    return render(request, "user_profile.html", {"user_obj": user_obj})

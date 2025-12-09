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
from .forms import EventForm, EventFilterForm
from .filters import filter_events
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt, csrf_protect 
from django.conf import settings
import os
import json
from datetime import date, timedelta
from django.contrib.auth.views import PasswordChangeView
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
    query = request.GET.get('q', '')
    
    today = datetime.today().date()  # only future or today
    if query:
        events_data = list(Events.objects.search(query))
    else:    
        events_data = list(Events.objects.filter(date__gte=today))  # <- only future events
    
    form = EventFilterForm(request.GET or None)
    if form.is_valid():
        events_data = filter_events(
            events_data,
            campus=form.cleaned_data.get('campus'),
            days=form.cleaned_data.get('days'),
            time_ranges=form.cleaned_data.get('time_range'),
            event_types=form.cleaned_data.get('event_type'),
        )
            
    # Sort by date and start_time
    events_data.sort(key=lambda e: (e.date, e.start_time_obj or datetime.min.time()))

    user_role = None
    user_favorites = []
    
    # User favorites
    if request.user.is_authenticated:
        try:
            user_obj = Users.objects.get(user=request.user)
            user_favorites = list(Favorites.objects.filter(user_ID=user_obj).values_list('event_ID__id', flat=True))
            user_role = user_obj.role
        except Users.DoesNotExist:
            user_favorites = []

    # ===== PAGINATION =====
    paginator = Paginator(events_data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'home.html', {
        'events_data': page_obj,
        'form': form,
        'user_favorites': user_favorites,
        'user_id': request.user.id if request.user.is_authenticated else None,
        'user_name': request.user.username if request.user.is_authenticated else None,
        'user_role': user_role, 
        'search_query': query, 
    })

def calendar_view(request):
    """
    Render calendar with favorite events per day for the logged-in user.
    Sends full event objects (name, type, campus, start/end times, location)
    so JS can generate pins.
    """
    events_per_day = {}  # key = YYYY-MM-DD, value = list of events

    if request.user.is_authenticated:
        try:
            user_obj = Users.objects.get(user=request.user)
            favorite_events = Favorites.objects.filter(user_ID=user_obj).select_related('event_ID')

            for fav in favorite_events:
                event = fav.event_ID
                event_date = event.date
                if not event_date:
                    continue  # skip if date is None

                day_key = event_date.strftime("%Y-%m-%d")

                if day_key not in events_per_day:
                    events_per_day[day_key] = []

                # Add full event info for JS
                events_per_day[day_key].append({
                    "name": event.name,
                    "event_type": getattr(event, "event_type", "General"),
                    "campus": getattr(event, "campus", ""),
                    "start_time": getattr(event, "start_time", ""),
                    "end_time": getattr(event, "end_time", ""),
                    "location": getattr(event, "location", "")
                })

        except Users.DoesNotExist:
            pass

    context = {
        "events_by_day": events_per_day,  # matches JS variable name
    }

    return render(request, "calendar.html", context)

def event_map(request):
    if request.user.is_authenticated:
        try:
            user_profile = Users.objects.get(user=request.user)
            # Get only events the user favorited
            interested_events = Events.objects.filter(favorites__user_ID=user_profile).distinct()
        except Users.DoesNotExist:
            interested_events = Events.objects.none()
    else:
        # Not logged in → no events
        interested_events = Events.objects.none()

    # Group events by campus
    pleasant_hill_events = interested_events.filter(campus="Pleasant Hill")
    san_ramon_events = interested_events.filter(campus="San Ramon")
    virtual_events = interested_events.filter(campus="Virtual")  # ← your guarantee

    # Convert all interested events to JSON for the map
    events_for_js = []
    for e in interested_events:
        coords = e.coordinates
        events_for_js.append({
            "id": e.id,
            "name": e.name,
            "date": e.date.strftime("%Y-%m-%d"),
            "building_code": e.building_code,
            "campus": e.campus,
            "lat": coords[0] if coords else None,
            "lng": coords[1] if coords else None,
        })

    return render(request, "event_map.html", {
        "events": events_for_js,
        "count_ph": pleasant_hill_events.count(),
        "count_sr": san_ramon_events.count(),
        "count_virtual": virtual_events.count(),
        "count_total": interested_events.count(),
    })

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
    user_profile = getattr(request.user, 'users', None)
    if not request.user.is_authenticated or not user_profile:
        messages.error(request, "Not Authorized.")
        return redirect('home')
    
    if user_profile.role  == "superuser":
        all_events = list(Events.objects.all())
    elif user_profile.role == "admin":
        all_events = list(Events.objects.filter(author_ID=user_profile))

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

    user_profile = getattr(request.user, 'users', None)

    if not request.user.is_authenticated or not user_profile:
        messages.error(request, "Not Authorized.")
        return redirect('home')

    if user_profile.role == "user" or (user_profile.role == 'admin' and event.author_ID != user_profile):
        messages.error(request, "You do not have permission to edit this event.")
        return redirect('home')

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated successfully.")
            return redirect('manage_events')
    else:
        form = EventForm(instance=event)

    return render(
        request,
        "event_form.html",
        {
            'event': event,
            'form': form,
            'page_title': 'Edit Event',
            'submit_text': 'Update Event'
        }
    )

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

        # Update biography and links
        biography = request.POST.get("biography", "").strip()
        links = request.POST.get("links", "").strip()
        profile_obj.biography = biography
        profile_obj.links = links

        # Update avatar if uploaded
        if "avatar" in request.FILES:
            # Delete old avatar if it exists
            if profile_obj.avatar_url and os.path.isfile(profile_obj.avatar_url.path):
                os.remove(profile_obj.avatar_url.path)
            # Save new avatar
            profile_obj.avatar_url = request.FILES["avatar"]

        # Save changes
        user_obj.save()
        profile_obj.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("user_profile")

    return render(request, "user_profile.html", {"user_obj": user_obj})

def profile_view(request):
    user_obj = User.objects.get(id=request.user.id)
    return render(request, 'profile.html', {'user_obj': user_obj})

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'password_change_form.html'
    success_url = reverse_lazy('user_profile')

    def form_valid(self, form):
        messages.success(self.request, "Your password has been successfully updated!")
        return super().form_valid(form)

    def form_invalid(self, form):
        # Collect all errors
        errors = []
        for field, field_errors in form.errors.items():
            errors.extend(field_errors)
        for error in errors:
            messages.error(self.request, error)
        return super().form_invalid(form)
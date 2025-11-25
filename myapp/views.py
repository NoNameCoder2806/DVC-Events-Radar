from django.shortcuts import render, redirect, get_object_or_404
from .models import Users, Events, Favorites
from django.contrib.auth.hashers import make_password, check_password

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
    data['user_id'] = request.session.get('user_id')
    data['user_name'] = request.session.get('user_name')
    return render(request, 'home.html', data)

def calendar(request):
    return render(request, 'calendar.html')

def map(request):
    return render(request, 'map.html')

def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            user = Users.objects.get(email=email)
            if check_password(password, user.password):
                # if password is correct
                # Store session info
                request.session['user_id'] = user.id
                request.session['user_name'] = f"{user.first_name} {user.last_name}"
                return redirect("home")  # successful login
            else:
                # if password is wrong
                # invalid login
                return render(request, 'login.html', {'error': 'Invalid credentials'})
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
            password = make_password(request.POST.get("password")),
            DVC_ID = request.POST.get("DVC_ID"),
            role = 'user'
        )
        user_register.save()
        return redirect("login")
    
def event_detail(request, event_id):
    event = get_object_or_404(Events, id=event_id)
    return render(request, "event_detail.html", {"event": event})
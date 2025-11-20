from django.shortcuts import render, redirect
from .models import Users, Events, Favorites

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
    return render(request, 'home.html', data)

def calendar(request):
    return render(request, 'calendar.html')

def map(request):
    return render(request, 'map.html')

def login(request):
    return render(request, 'login.html')

def register(request):
    if request.method == "GET":
        data = get_data()
        return render(request, 'register.html', data)
    elif request.method == "POST":
        user_register = Users(first_name =  request.POST.get("first_name"), last_name = request.POST.get("last_name"), email = request.POST.get("email"), password = request.POST.get("password"), DVC_ID = request.POST.get("DVC_ID"), role = 'user')
        user_register.save()
        return redirect("login")
from django.shortcuts import render
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
    return render(request, 'register.html')
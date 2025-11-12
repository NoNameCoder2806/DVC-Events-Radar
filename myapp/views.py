from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def calendar(request):
    return render(request, 'calendar.html')

def map(request):
    return render(request, 'map.html')

def login(request):
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')
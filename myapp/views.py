from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def calendar(request):
    return render(request, 'calendar.html')

def map(request):
    return render(request, 'map.html')
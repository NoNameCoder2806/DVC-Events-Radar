from django.contrib import admin
from .models import Users, Events, Favorites

# Register your models here.
admin.site.register(Users)
admin.site.register(Events)
admin.site.register(Favorites)
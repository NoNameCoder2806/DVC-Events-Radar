from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import Users, Events, Favorites
from datetime import datetime

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        password_validation = cleaned_data.get('password_validation')

        if not email:
            self.add_error('email', 'email is required')

        if not password:
            self.add_error('password', 'password is required')

        if password_validation and password and password != password_validation:
            self.add_error('password_validation', "passwords don't match")

        return cleaned_data
        
class EventForm(forms.ModelForm):
    class Meta:
        model = Events
        fields = ['name', 'description', 'date', 'start_time', 'end_time', 'location', 'campus', 'event_type', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}), 
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), 
            'start_time' : forms.TextInput(attrs={'placeholder': 'HH:MM AM/PM', 'class': 'form-control'}), 
            'end_time' : forms.TextInput(attrs={'placeholder': 'HH:MM AM/PM', 'class': 'form-control'}), 
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'campus': forms.Select(attrs={'class': 'form-control'}),
            'event_type': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),     
        }
        
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        
        if start_time and end_time:
            try: 
                start_obj = datetime.strptime(start_time.strip(), "%I:%M %p")
                end_obj = datetime.strptime(end_time.strip(), "%I:%M %p")
                if start_obj >= end_obj:
                    raise forms.ValidationError("Start time must be before end time")            
            except ValueError:
                raise forms.ValidationError("Time format must be HH:MM AM/PM")
        return cleaned_data 
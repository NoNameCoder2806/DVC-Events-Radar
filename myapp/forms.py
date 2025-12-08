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

HOURS = [(str(i), str(i)) for i in range(1, 13)]
MINUTES = [(f"{i:02}", f"{i:02}") for i in range(0, 60)]
PERIODS = [('AM', 'AM'), ('PM', 'PM')]

class EventForm(forms.ModelForm):
    start_hour = forms.ChoiceField(choices=HOURS)
    start_minute = forms.ChoiceField(choices=MINUTES)
    start_period = forms.ChoiceField(choices=PERIODS)
    
    end_hour = forms.ChoiceField(choices=HOURS)
    end_minute = forms.ChoiceField(choices=MINUTES)
    end_period = forms.ChoiceField(choices=PERIODS)

    class Meta:
        model = Events
        fields = ['name', 'description', 'date', 'location', 'campus', 'event_type', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'campus': forms.Select(attrs={'class': 'form-control'}),
            'event_type': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        # Combine hours, minutes, and period into time objects
        from datetime import datetime

        start_h = cleaned_data.get('start_hour')
        start_m = cleaned_data.get('start_minute')
        start_p = cleaned_data.get('start_period')
        end_h = cleaned_data.get('end_hour')
        end_m = cleaned_data.get('end_minute')
        end_p = cleaned_data.get('end_period')

        if start_h and start_m and start_p and end_h and end_m and end_p:
            start_time_str = f"{start_h}:{start_m} {start_p}"
            end_time_str = f"{end_h}:{end_m} {end_p}"
            try:
                start_obj = datetime.strptime(start_time_str, "%I:%M %p")
                end_obj = datetime.strptime(end_time_str, "%I:%M %p")
                if start_obj >= end_obj:
                    raise forms.ValidationError("Start time must be before end time")
            except ValueError:
                raise forms.ValidationError("Invalid time format")
        
        return cleaned_data
        
class EventFilterForm(forms.Form):
    CAMPUS_CHOICES = [('Pleasant Hill', 'Pleasant Hill'),('San Ramon', 'San Ramon'),('Virtual', 'Virtual')]
    DAYS_OF_WEEK = [('Monday','Monday'),('Tuesday','Tuesday'),('Wednesday','Wednesday'),('Thursday','Thursday'),('Friday','Friday'),('Saturday','Saturday'),('Sunday','Sunday')]
    TIME_RANGES = [('Morning', 'Morning (8am-12pm)'),('Afternoon','Afternoon (12pm-5pm)'), ('Evening', 'Evening (5pm-9pm)')]
    EVENT_TYPES = [('Sports', 'Sports'), ('Clubs', 'Clubs'),('Carrer & Academic', 'Career & Academic'), ('Free Food', 'Free Food'), ('General', 'General')]    
    
    campus = forms.MultipleChoiceField(choices=CAMPUS_CHOICES,  required=False, widget=forms.CheckboxSelectMultiple())
    days = forms.MultipleChoiceField(choices=DAYS_OF_WEEK,  required=False, widget=forms.CheckboxSelectMultiple())
    time_range = forms.MultipleChoiceField(choices=TIME_RANGES,  required=False, widget=forms.CheckboxSelectMultiple())
    event_type = forms.MultipleChoiceField(choices=EVENT_TYPES,  required=False, widget=forms.CheckboxSelectMultiple())
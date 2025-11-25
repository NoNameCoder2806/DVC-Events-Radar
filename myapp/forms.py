from django import forms
from django.forms import ModelForm
from .models import Users, Events, Favorites

class PostForm(ModelForm):
    class Meta:
        model = Users
        fields = ['first_name', 'last_name', 'email', 'password', 'password_validation', 'DVC_ID']

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
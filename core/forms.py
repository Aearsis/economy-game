from django.contrib import auth
import django.contrib.auth.forms
from django import forms

from .models import *

class AuthenticationForm(auth.forms.AuthenticationForm):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    username = forms.CharField(max_length=254, label="Uživatelské jméno" )
    password = forms.CharField(label="Heslo", widget=forms.PasswordInput)

    error_messages = {
        'invalid_login': "Uživatelské jméno nebo heslo je nesprávné."
    }

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = [ 'name', 'members' ]
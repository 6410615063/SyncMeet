from django import forms
from .models import UserInfo
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm

class ImageForm(forms.ModelForm):
    # Form for the image model
    class Meta:
        model = UserInfo
        fields = ('profile_image', )

class PasswordChangingForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'type': 'password'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'type': 'password'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'type': 'password'}))
    class Meta:
        Model = User
        fields = ('old_password', 'new_password1', 'new_password2')

from django import forms
from .models import UserInfo


class ImageForm(forms.ModelForm):
    # Form for the image model
    class Meta:
        model = UserInfo
        fields = ('profile_image', )

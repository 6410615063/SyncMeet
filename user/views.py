from django.shortcuts import render, redirect
from user.models import *
from django.http import HttpResponseRedirect, HttpResponse
# from twilio.rest import Client
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import UserInfo
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

account_sid = "AC3607d951e9f16551ff392e66a5086414"
auth_token = "4d251cb5cbb2b470be11874ace98e0f5"
verify_sid = "VAc62028483f915539917bf2ee4e83b839"


def profile(request):
    user = User.objects.get(username=request.user.username)
    user_info = UserInfo.objects.get(user_id=user)
    context = {'userInfo': user_info}

    return render(request, 'user/profile.html', context)

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
from .models import UserInfo, Friend
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


def edit_profile(request):
    if not request.user.is_authenticated:
        return render(request, 'users/signin.html', status=403)

    user = User.objects.get(username=request.user.username)
    user_info = UserInfo.objects.get(user_id=user)
    context = {'userInfo': user_info}

    if request.method == "POST":
        username = request.POST.get('username')
        sir_name = request.POST.get('sir_name')
        gender = request.POST.get('gender')
        age = request.POST.get('age')
        contact = request.POST.get('contact')

        # ตรวจสอบการอัปโหลดรูปภาพ
        if 'profile_image' in request.FILES:
            profile_image = request.FILES['profile_image']
            user_info.profile_image = profile_image
            user_info.save()

        # อัปเดตข้อมูลโปรไฟล์
        user_info.user_id.username = username
        user_info.sir_name = sir_name
        user_info.gender = gender
        user_info.age = age
        user_info.contact = contact
        user_info.save()

        return redirect('/')

    return render(request, 'user/editprofile.html', context)


def friend_list(request, user_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user:signin'))

    userInfo = UserInfo.objects.get(account_UID=user_id)
    all_friend = Friend.objects.filter(user_id=userInfo, status=True)

    return render(request, 'user/friendlist.html', {
        'all_friend': all_friend,
    })

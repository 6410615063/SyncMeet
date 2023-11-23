from django.http import HttpResponse
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
from django.urls import reverse
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from user.form import PasswordChangingForm

from django.contrib import messages

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

    user = User.objects.get(username=request.user.username)
    user_info = UserInfo.objects.get(user_id=user)

    userInfo = UserInfo.objects.get(account_UID=user_id)
    all_friend = Friend.objects.filter(user_id=userInfo, status=True)

    context = {
        'userInfo': user_info,
        'all_friend': all_friend,
    }

    return render(request, 'user/friendlist.html', context)


def change_password(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user:signin'))
    if request.method == 'POST':
        form = PasswordChangingForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('user:profile')
        else:
            form_class = PasswordChangingForm(user=request.user)
            return render(request, 'user/changepassword.html', {'form': form_class, 'message': "Invalid password"})
    else:
        form_class = PasswordChangingForm(user=request.user)
        return render(request, 'user/changepassword.html', {'form': form_class})
    # เพิ่มข้อมูลเพิ่มเติมใน context
    context['all_friend'] = all_friend

    return render(request, 'user/friendlist.html', context)


def add_friend(request):
    user = User.objects.get(username=request.user.username)
    user_info = UserInfo.objects.get(user_id=user)
    context = {'userInfo': user_info}

    if request.method == 'POST':
        user_account_UID = request.POST.get(
            'user_account_UID')  # เลข account_UID ของผู้ใช้
        # เลข account_UID ของเพื่อนที่ต้องการเพิ่ม
        friend_account_UID = request.POST.get('friend_account_UID')

        userInfo = UserInfo.objects.get(account_UID=user_account_UID)
        all_friend = Friend.objects.filter(user_id=userInfo, status=True)

        # เพิ่มข้อมูลเพิ่มเติมใน context
        context['all_friend'] = all_friend

        try:
            user_info = UserInfo.objects.get(account_UID=user_account_UID)
            friend_info = UserInfo.objects.get(account_UID=friend_account_UID)

            # สร้างเพื่อน
            friend, created = Friend.objects.get_or_create(
                user_id=user_info, friend_id=friend_info, defaults={'status': True})

            friend, created = Friend.objects.get_or_create(
                user_id=friend_info, friend_id=user_info, defaults={'status': True})

            if created:
                context['message'] = 'Friend added successfully!'

            else:
                context['message'] = f'{friend_info.user_id.username} is already a friend of {user_info.user_id.username}'

        except UserInfo.DoesNotExist:
            context['message'] = 'User UID not found!'

        except Friend.MultipleObjectsReturned:
            context['message'] = 'Multiple friends found! Something went wrong.'
    else:
        context['message'] = 'Invalid request method!'

    return render(request, 'user/friendlist.html', context)


def delete_friend(request):

    user = User.objects.get(username=request.user.username)
    user_info = UserInfo.objects.get(user_id=user)
    context = {'userInfo': user_info}

    if request.method == 'POST':
        user_account_UID = request.POST.get(
            'user_account_UID')  # เลข account_UID ของผู้ใช้
        # เลข account_UID ของเพื่อนที่ต้องการเพิ่ม
        friend_account_UID = request.POST.get('friend_account_UID')

        userInfo = UserInfo.objects.get(account_UID=user_account_UID)
        all_friend = Friend.objects.filter(user_id=userInfo, status=True)

        # เพิ่มข้อมูลเพิ่มเติมใน context
        context['all_friend'] = all_friend

        user_info = UserInfo.objects.get(account_UID=user_account_UID)
        friend_info = UserInfo.objects.get(account_UID=friend_account_UID)

        friend = get_object_or_404(
            Friend, user_id=user_info, friend_id=friend_info)
        friend.delete()

        friend_re = get_object_or_404(
            Friend, user_id=friend_info, friend_id=user_info)
        friend_re.delete()

    return render(request, 'user/friendlist.html', context)

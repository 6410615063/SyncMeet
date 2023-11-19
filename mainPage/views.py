from django.http import HttpResponseRedirect
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from user.models import UserInfo
from groups.models import GROUP_TAG, Group

from mainPage.models import Activity

from mainPage.function import printTest, getTableSlot
# Create your views here.
import random


def generate_unique_account_UID():
    while True:
        # สร้างเลขสุ่ม 6 หลัก
        new_account_UID = random.randint(100000, 999999)

        # ตรวจสอบในฐานข้อมูลว่ามีเลขนี้ซ้ำหรือไม่
        exists = UserInfo.objects.filter(account_UID=new_account_UID).exists()

        # ถ้าไม่มีให้ return เลขที่สร้างขึ้นใหม่
        if not exists:
            return new_account_UID


@login_required(login_url='login')
def IndexPage(request):
    return render(request, 'mainPage/index.html')


def SignupPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')
        if pass1 != pass2 or pass1 is None or pass2 is None:
            return render(request, 'mainPage/signup.html', {
                'message': 'Your password and confrom password are not same!'
            })
        else:
            if User.objects.filter(username=username).first():
                return render(request, 'mainPage/signup.html', {
                    'message': 'Already have username!'
                })
            my_user = User.objects.create_user(
                username=username, password=pass1)
            my_user.save()

            # สร้าง account_UID โดยใช้ฟังก์ชันที่สร้างขึ้นด้านบน
            new_account_UID = generate_unique_account_UID()

            user_info = UserInfo.objects.create(
                user_id=my_user,
                account_UID=new_account_UID,
                sir_name=request.POST.get('sir_name', '-'),
                gender=request.POST.get('gender', 'other'),
                age=request.POST.get('age', 0),
                contact=request.POST.get('contact', '-'),
                # Ensure you handle 'profile_image' separately, as it's an image upload
            )

            # Handle profile image separately (if provided in the form)
            profile_image = request.FILES.get('profile_image')
            if profile_image:
                user_info.profile_image = profile_image
                user_info.save()

            return redirect('login')
    return render(request, 'mainPage/signup.html')


def LoginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('pass')
        user = authenticate(request, username=username, password=pass1)
        if user is not None:
            login(request, user)
            return redirect('group')
        else:
            return render(request, 'mainPage/login.html', {
                'message': 'Username or Password is Incorrect!'
            })

    return render(request, 'mainPage/login.html')


def LogoutPage(request):
    logout(request)
    return redirect('login')


def AboutPage(request):
    return render(request, 'mainPage/about.html')


@login_required(login_url='login')
def group(request):
    if request.user.is_staff:
        return HttpResponseRedirect(reverse('admin:index'))

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    group_filter = request.GET.get('gname', '')
    tag_filter = request.GET.get('gtag', '')

    groups = Group.objects.filter(
        gmembers=request.user, gname__icontains=group_filter, gtag__icontains=tag_filter).order_by('gname')
    return render(request, 'groups/group.html', {'groups': groups, 'GROUP_TAG': GROUP_TAG})


def UserSchedule(request):
    activity = Activity.objects.filter(user=request.user)
    table_slot = getTableSlot(activity)
    timeRange = [str(hour) + ":00" for hour in range(24)]
    return render(request, 'mainPage/schedule_user.html', {
        'activity': activity,
        'timeRange': timeRange,
        'slot_sunday': table_slot[0],
        'slot_monday': table_slot[1],
        'slot_tuesday': table_slot[2],
        'slot_wednesday': table_slot[3],
        'slot_thursday': table_slot[4],
        'slot_friday': table_slot[5],
        'slot_saturday': table_slot[6],
    }
    )


def EditSchedule(request):
    activity = Activity.objects.filter(user=request.user)

    if request.method == 'POST':
        start_day = request.POST.get('start_day')
        start_time = request.POST.get('start_time')
        end_day = request.POST.get('end_day')
        end_time = request.POST.get('end_time')
        id = Activity.objects.last().activityId + 1
        while Activity.objects.filter(activityId=id):
            id += 1
        new_activity = Activity.objects.create(user=request.user, activityId=id,
                                               start_day=start_day, start=start_time,
                                               end_day=end_day, end=end_time)
        new_activity.save()
    return render(request, 'mainPage/edit_schedule.html', {
        'activity': activity,
    }
    )


def RemoveActivity(request, activityId):
    Activity.objects.filter(user=request.user, activityId=activityId).delete()
    return redirect('edit_schedule')

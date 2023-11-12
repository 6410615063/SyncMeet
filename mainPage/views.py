from django.http import HttpResponseRedirect
from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from groups.models import GROUP_TAG, Group

from mainPage.models import Activity

from mainPage.function import printTest, getTableSlot
# Create your views here.
@login_required(login_url='login')
def IndexPage(request):
    return render(request, 'mainPage/index.html')


def SignupPage(request):
    if request.method=='POST':
        username=request.POST.get('username')
        pass1=request.POST.get('password1')
        pass2=request.POST.get('password2')
        if pass1!=pass2 or pass1 is None or pass2 is None:
            return render(request, 'mainPage/signup.html', {
                'message': 'Your password and confrom password are not same!'
            })
        else:
            if User.objects.filter(username = username).first():
                return render(request, 'mainPage/signup.html', {
                'message': 'Already have username!'
                })
            my_user=User.objects.create_user(username=username, password=pass1)
            my_user.save()
            return redirect('login')
    return render(request, 'mainPage/signup.html')


def LoginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('pass')
        user = authenticate(request, username=username, password=pass1)
        if user is not None:
            login(request,user)
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

    groups = Group.objects.filter(gmembers=request.user, gname__icontains=group_filter, gtag__icontains=tag_filter).order_by('gname')
    return render(request, 'group.html', {'groups': groups, 'GROUP_TAG': GROUP_TAG})

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

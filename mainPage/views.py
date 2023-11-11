from django.http import HttpResponseRedirect
from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from groups.models import GROUP_TAG, Group

# Create your views here.
# @login_required(login_url='login')
# def IndexPage(request):
#     return render(request, 'mainPage/index.html')

def SignupPage(request):
    if request.method=='POST':
        username=request.POST.get('username')
        email=request.POST.get('email')
        pass1=request.POST.get('password1')
        pass2=request.POST.get('password2')
        if pass1!=pass2:
            return HttpResponse("Your password and confrom password are not Same!!")
        else:
            my_user=User.objects.create_user(username,email,pass1)
            my_user.save()
            return redirect('login')
    return render (request,'mainPage/signup.html')

def LoginPage(request):
    if request.method=='POST':
        username=request.POST.get('username')
        pass1=request.POST.get('pass')
        user=authenticate(request,username=username,password=pass1)
        if user is not None:
            login(request,user)
            return redirect('group')
        else:
            return HttpResponse ("Username or Password is incorrect!!!")

    return render (request,'mainPage/login.html')

def LogoutPage(request):
    logout(request)
    return redirect('login')

def about(request):
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
from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required

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
            return HttpResponse("Your password and confrom password are not Same!!")
        else:
            if User.objects.filter(username = username).first():
                return HttpResponse("Already have username!!")
            my_user=User.objects.create_user(username,pass1)
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
            return redirect('index')
        else:
            return HttpResponse ("Username or Password is incorrect!!!")

    return render (request,'mainPage/login.html')

def LogoutPage(request):
    logout(request)
    return redirect('login')

def about(request):
    return render(request, 'mainPage/about.html')

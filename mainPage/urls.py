from django.urls import path, include
from . import views

urlpatterns = [
    path('',views.IndexPage, name='index'),
    path('login/', views.LoginPage, name='login'),
    path('signup/',views.SignupPage, name='signup'),
    path('logout/',views.LogoutPage, name='logout'),
    path('about', views.about, name="about"),
    path('/group, views.GroupListPage, name="group"'),
    path('/schedule, views.UserSchedule, name="schedule_user"'),

]
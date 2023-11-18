from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.group, name='group'),
    path('login/', views.LoginPage, name='login'),
    path('signup/', views.SignupPage, name='signup'),
    path('logout/', views.LogoutPage, name='logout'),
    path('about', views.AboutPage, name="about"),
    path('group', views.group, name="group"),
    path('schedule', views.UserSchedule, name="schedule_user"),
    path('schedule/edit_schedule', views.EditSchedule, name="edit_schedule"),
    path('schedule/edit_schedule/<int:activityId>/remove', 
            views.RemoveActivity, name="remove_activity"),

]

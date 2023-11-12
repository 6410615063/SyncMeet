from django.urls import path, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

app_name = 'user'

urlpatterns = [


    path('profile/', views.profile, name='profile'),

]

from django.urls import path, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

app_name = 'user'
urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('friendlist/<int:user_id>', views.friend_list, name='friend_list'),
    path('change_password/', views.change_password, name='change_password'),
    path('add_friend/', views.add_friend, name='add_friend'),
]

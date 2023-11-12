from . import views
from django.urls import path, include

urlpatterns = [
    path('create_group/', views.create_group, name='create_group'),
    path('group/<int:group_id>/', views.group_schedule, name='group_schedule'),
    path('group/<int:group_id>/members', views.group_members, name='group_members'),
    path('group/<int:group_id>/post/', views.post, name='post'),
    path('group/<int:group_id>/create_post/', views.create_post, name='create_post'),
    path('group/<int:group_id>/delete_post/', views.delete_post, name='delete_post'),
    path('group/<int:group_id>/leave/', views.leave_group, name='leave_group'),
    path('user/', include('user.urls')),
]
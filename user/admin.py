from django.contrib import admin
from user.models import UserInfo, Friend
# Register your models here.


class UserInfoAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'account_UID', 'profile_image', 'prefix_phone_number',
                    'phone_number', 'sir_name', 'gender', 'age', 'contact')


class FriendAdmin(admin.ModelAdmin):
    list_display = ("user_id", "friend_id", "status")


admin.site.register(UserInfo, UserInfoAdmin)
admin.site.register(Friend, FriendAdmin)

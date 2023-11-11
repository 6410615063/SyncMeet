from django.contrib import admin

# Register your models here.
from .models import Activity

class ActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activityId', 'start', 'start_day', 'end', 'end_day')

admin.site.register(Activity, ActivityAdmin)
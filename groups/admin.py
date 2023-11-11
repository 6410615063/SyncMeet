from django.contrib import admin
from .models import Group, Post

# Register your models here.

class GroupAdmin(admin.ModelAdmin):
    list_display = ('gname', 'gtag', 'gcreator')

class PostAdmin(admin.ModelAdmin):
    list_display = ('ptitle', 'pauthor', 'pcreated_on')

admin.site.register(Group, GroupAdmin)
admin.site.register(Post, PostAdmin)
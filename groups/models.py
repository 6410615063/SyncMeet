from django.db import models
from django.contrib.auth.models import User

# Create your models here.

GROUP_TAG = (
    ('Untitled', 'Untitled'),
    ('Education', 'Education'),
    ('Travel', 'Travel'),
    ('Work', 'Work'),
    ('Sports', 'Sports'),
    ('Food', 'Food'),
    ('Reading', 'Reading'),
    ('Art', 'Art'),
    ('Pets', 'Pets'),    
    ('Movies', 'Movies'),
    ('Music', 'Music'),
    ('Health', 'Health'),
    ('Technology', 'Technology'),
)

class Group(models.Model):
    gname = models.CharField(max_length=100)
    gdescription = models.TextField()
    gprofile = models.ImageField(upload_to='group_profiles/', blank=True, null=True)
    gtag = models.CharField(max_length=20, choices=GROUP_TAG, default='Untitled')
    gmembers = models.ManyToManyField(User, related_name='group_members')
    gcreator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_creator')

    def is_creator(self, user):
        return self.gcreator == user
    
    def __str__(self):
        return self.gname
    

POST_TAG = (
    ('Untitled', 'Untitled'),
    ('Education', 'Education'),
    ('Travel', 'Travel'),
    ('Work', 'Work'),
    ('Sports', 'Sports'),
    ('Food', 'Food'),
    ('Reading', 'Reading'),
    ('Art', 'Art'),
    ('Pets', 'Pets'),    
    ('Movies', 'Movies'),
    ('Music', 'Music'),
    ('Health', 'Health'),
    ('Technology', 'Technology'),
)

class Post(models.Model):
    ptitle = models.CharField(max_length=100)
    pauthor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_post')
    pcontent = models.TextField()
    ptag = models.CharField(max_length=20, choices=POST_TAG, default='Untitled')
    pgroup = models.ForeignKey(Group, on_delete=models.CASCADE)
    pcreated_on = models.DateTimeField(auto_now_add=True)

    def formatted_date(self):
        return self.pcreated_on.strftime('%d %B %Y %I:%M %p')
    
    def __str__(self):
        return self.ptitle
from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    activityId = models.PositiveIntegerField(unique=True)
    
    DAYS_CHOICES = (
                    ('Monday','Monday'),
                    ('Tuesday','Tuesday'),
                    ('Wednesday','Wednesday'),
                    ('Thursday','Thursday'),
                    ('Friday','Friday'),
                    ('Saturday','Saturday'),
                    ('Saturday','Saturday'),
                    )
    start = models.TimeField()
    start_day = models.CharField(max_length=9, choices=DAYS_CHOICES)
    end = models.TimeField()
    end_day = models.CharField(max_length=9, choices=DAYS_CHOICES)

    def __str__(self):
        return "From"

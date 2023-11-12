from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from user.models import UserInfo
from django.template.exceptions import TemplateDoesNotExist

from django.db.utils import IntegrityError
# Create your tests here.

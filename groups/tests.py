from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from user.models import UserInfo
from django.template.exceptions import TemplateDoesNotExist

from django.db.utils import IntegrityError
# Create your tests here.

class UserTest(TestCase):
    def setUp(self) -> None:
        user = User.objects.create_user(username='test1', password='12345')
        user.save()

    def test_Group_login(self):
        c = Client()
        c.post(reverse('login'),{'username':'test1','pass':'12345'})
        response = c.get(reverse('group'))
        self.assertEqual(response.status_code, 200)

    def test_Group_notLogin(self):
        c = Client()
        response = c.get(reverse('group'))
        self.assertEqual(response.status_code, 302)

    def test_create_group(self):
        c = Client()
        c.post(reverse('login'),{'username':'test1','pass':'12345'})
        response = c.post(reverse('create_group'),{'gname':'a', 'gdescription':'a', 
                            'gtag':'a', })
        self.assertEqual(response.status_code, 302)

    def test_create_group_emptyForm(self):
        c = Client()
        c.post(reverse('login'),{'username':'test1','pass':'12345'})
        self.assertRaises(TemplateDoesNotExist, c.post, reverse('create_group'),
                            {'gname':'', 'gdescription':'', 'gtag':'', })        
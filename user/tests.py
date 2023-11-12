from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from user.models import UserInfo

from django.db.utils import IntegrityError
# Create your tests here.

class UserTest(TestCase):
    def setUp(self) -> None:
        user = User.objects.create_user(username='test1', password='12345')
        user.save()

    def test_UserProfile_notLogin(self):
        c = Client()
        self.assertRaises(User.DoesNotExist, c.get, '/user/profile/')

    def test_UserProfile_no_UserInfo(self):
        c = Client()
        c.post(reverse('login'),{'username':'test1','pass':'12345'})
        self.assertRaises(UserInfo.DoesNotExist, c.get, '/user/profile/')

    def test_UserProfile_has_UserInfo(self):
        c = Client()
        user = User.objects.create_user(username='test6', password='12345')
        c.post(reverse('login'),{'username':'test6','pass':'12345'})
        UserInfo.objects.create(user_id=user, account_UID=1, age=20, 
                                contact="https://www.facebook.com/",
                                gender="Male", phone_number="00")
        response = c.get('/user/profile/')
        self.assertEqual(response.status_code, 200)
        
    def test_UserInfo_duplicate_UID(self):
        user1 = User.objects.create_user(username='test2', password='12345')
        user2 = User.objects.create_user(username='test3', password='12345')
        UserInfo.objects.create(account_UID=1, user_id=user1, age=20)
        self.assertRaises(IntegrityError, UserInfo.objects.create, account_UID=1, user_id=user2, age=20)
        
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from mainPage.models import Activity
from django.db.utils import IntegrityError
import datetime, time
# Create your tests here.


class UserTest(TestCase):
    def setUp(self) -> None:
        user = User.objects.create_user(username='test1', password='12345')
        user.save()
    
    def test_ValidCreateUser(self):
        c = Client()
        response = c.post(reverse('signup'),{'username':'test2','password1':'12345', 'password2':'12345'})
        self.assertEqual(response.status_code, 302)
    
    def test_InValidCreateUser_MissingPassword(self):
        c = Client()
        response = c.post(reverse('signup'),{'username':'test2','password1':'12345'})
        self.assertEqual(response.status_code, 200)
    
    
    def test_InValidCreateUser_MissingUsername(self):
        c = Client()
        #response = c.post(reverse('signup'),{'password1':'12345', 'password2':'12345'})
        #self.assertEqual(response.status_code, 200)
        self.assertRaises(ValueError, c.post, reverse('signup'),{'password1':'12345', 'password2':'12345'})

    def test_InValidCreateUser_DuplicateUsername(self):
        c = Client()
        response = c.post(reverse('signup'),{'username':'test1','password1':'12345', 'password2':'12345'})
        self.assertEqual(response.status_code, 200)

    def test_Userlogin(self):
        c = Client()
        response = c.post(reverse('login'),{'username':'test1','pass':'12345'})
        self.assertEqual(response.status_code, 302)

    def test_InvalidUserlogin_WrongUsername(self):
        c = Client()
        response = c.post(reverse('login'),{'username':'test5','pass':'12345'})
        self.assertEqual(response.status_code, 200)

    def test_Logout(self):
        c = Client()
        c.post(reverse('login'),{'username':'test5','pass':'12345'})
        response = c.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
    
    def test_UserSchedule_notLogin(self):
        c = Client()
        #response = c.get(reverse('schedule_user'))
        #self.assertEqual(response.status_code, 200)
        self.assertRaises(TypeError, c.get, reverse('schedule_user'))

    def test_UserSchedule_empty(self):
        c = Client()
        c.post(reverse('login'),{'username':'test1','pass':'12345'})
        response = c.get(reverse('schedule_user'))
        self.assertEqual(response.status_code, 200)

    def test_UserSchedule_not_empty(self):
        c = Client()
        user = User.objects.create_user(username='test6', password='12345')
        c.post(reverse('login'),{'username':'test6','pass':'12345'})
        Activity.objects.create(user=user, activityId=1, start=datetime.datetime(2020, 5, 5, 10), start_day='Monday', end=datetime.datetime(2020, 5, 6, 10), end_day='Tuesday')
        response = c.get(reverse('schedule_user'))
        self.assertEqual(response.status_code, 200)
        
    
    def test_Activity_duplicate_activityId(self):
        c = Client()
        user = User.objects.create_user(username='test6', password='12345')
        c.post(reverse('login'),{'username':'test6','pass':'12345'})
        Activity.objects.create(user=user, activityId=1, start=datetime.datetime(2020, 5, 5, 10), start_day='Monday', end=datetime.datetime(2020, 5, 6, 10), end_day='Tuesday')
        #Activity.objects.create(user=user, activityId=1, start=datetime.datetime(2020, 5, 5, 10), start_day='Monday', end=datetime.datetime(2020, 5, 6, 10), end_day='Tuesday')
        self.assertRaises(IntegrityError, Activity.objects.create, user=user, activityId=1, start=datetime.datetime(2020, 5, 5, 10), start_day='Monday', end=datetime.datetime(2020, 5, 6, 10), end_day='Tuesday')
        

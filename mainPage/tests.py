from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from mainPage.models import Activity
from django.db.utils import IntegrityError
import datetime
import time
# Create your tests here.


class UserTest(TestCase):
    def setUp(self) -> None:
        user = User.objects.create_user(username='test1', password='12345')
        user.save()

    def test_ValidCreateUser(self):
        c = Client()
        response = c.post(reverse('signup'), {
                          'username': 'test2', 'password1': '12345', 'password2': '12345'})
        self.assertEqual(response.status_code, 302)

    def test_InValidCreateUser_MissingPassword(self):
        c = Client()
        response = c.post(reverse('signup'), {
                          'username': 'test2', 'password1': '12345'})
        self.assertEqual(response.status_code, 200)

    def test_InValidCreateUser_PasswordDontMatch(self):
        c = Client()
        response = c.post(reverse('signup'), {
                          'username': 'test2', 'password1': '12345', 'password2': '123456'})
        self.assertEqual(response.status_code, 200)

    def test_InValidCreateUser_MissingUsername(self):
        c = Client()
        self.assertRaises(ValueError, c.post, reverse('signup'), {
                          'password1': '12345', 'password2': '12345'})

    def test_InValidCreateUser_DuplicateUsername(self):
        c = Client()
        response = c.post(reverse('signup'), {
                          'username': 'test1', 'password1': '12345', 'password2': '12345'})
        self.assertEqual(response.status_code, 200)

    def test_Userlogin(self):
        c = Client()
        response = c.post(reverse('login'), {
                          'username': 'test1', 'pass': '12345'})
        self.assertEqual(response.status_code, 302)

    def test_InvalidUserlogin_WrongUsername(self):
        c = Client()
        response = c.post(reverse('login'), {
                          'username': 'test5', 'pass': '12345'})
        self.assertEqual(response.status_code, 200)

    def test_InvalidUserlogin_WrongPassword(self):
        c = Client()
        response = c.post(reverse('login'), {
                          'username': 'test1', 'pass': '123456'})
        self.assertEqual(response.status_code, 200)

    def test_Logout(self):
        c = Client()
        c.post(reverse('login'), {'username': 'test5', 'pass': '12345'})
        response = c.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)


class UserScheduleTest(TestCase):
    def setUp(self) -> None:
        user = User.objects.create_user(username='test1', password='12345')
        user.save()

    def test_UserSchedule_notLogin(self):
        c = Client()
        self.assertRaises(TypeError, c.get, reverse('schedule_user'))

    def test_UserSchedule_empty(self):
        c = Client()
        c.post(reverse('login'), {'username': 'test1', 'pass': '12345'})
        response = c.get(reverse('schedule_user'))
        self.assertEqual(response.status_code, 200)

    def test_UserSchedule_not_empty(self):
        c = Client()
        user = User.objects.create_user(username='test6', password='12345')
        c.post(reverse('login'), {'username': 'test6', 'pass': '12345'})
        Activity.objects.create(user=user, activityId=1, start=datetime.datetime(
            2020, 5, 5, 10), start_day='Monday', end=datetime.datetime(2020, 5, 6, 10), end_day='Tuesday')
        response = c.get(reverse('schedule_user'))
        self.assertEqual(response.status_code, 200)

    def test_Activity_duplicate_activityId(self):
        c = Client()
        user = User.objects.create_user(username='test6', password='12345')
        c.post(reverse('login'), {'username': 'test6', 'pass': '12345'})
        Activity.objects.create(user=user, activityId=1, start=datetime.datetime(
            2020, 5, 5, 10), start_day='Monday', end=datetime.datetime(2020, 5, 6, 10), end_day='Tuesday')
        self.assertRaises(IntegrityError, Activity.objects.create, user=user, activityId=1, start=datetime.datetime(
            2020, 5, 5, 10), start_day='Monday', end=datetime.datetime(2020, 5, 6, 10), end_day='Tuesday')

    def test_Activity_start_end_sameDay(self):
        c = Client()
        user = User.objects.create_user(username='test6', password='12345')
        c.post(reverse('login'), {'username': 'test6', 'pass': '12345'})
        Activity.objects.create(user=user, activityId=1,
                                start=datetime.datetime(2020, 5, 5, 10, 15, 30), start_day='Monday',
                                end=datetime.datetime(2020, 5, 5, 10, 20, 30), end_day='Monday')
        response = c.get(reverse('schedule_user'))
        self.assertEqual(response.status_code, 200)

    def test_Activity_end_before_start(self):
        c = Client()
        user = User.objects.create_user(username='test6', password='12345')
        c.post(reverse('login'), {'username': 'test6', 'pass': '12345'})
        Activity.objects.create(user=user, activityId=1,
                                start=datetime.datetime(2020, 5, 5, 10, 15, 30), start_day='Friday',
                                end=datetime.datetime(2020, 5, 5, 10, 20, 30), end_day='Monday')
        response = c.get(reverse('schedule_user'))
        self.assertEqual(response.status_code, 200)

    def test_editSchedule_add_activity(self):
        c = Client()
        user = User.objects.create_user(username='test6', password='12345')
        c.login(username='test6', password='12345')
        response = c.post(reverse('edit_schedule'), {'start_day': 'Monday', 'start_time': '10:30',
                                                     'end_day': 'Friday', 'end_time': '10:30'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Activity.objects.filter(
            user=user, start_day='Monday', end_day='Friday'))

    def test_editSchedule_incomplete_form(self):
        c = Client()
        user = User.objects.create_user(username='test6', password='12345')
        c.login(username='test6', password='12345')
        self.assertRaises(IntegrityError, c.post, reverse('edit_schedule'), {'start_day': 'Monday',
                                                                             'end_day': 'Friday'})

    def test_editSchedule_delete_activity(self):
        c = Client()
        user = User.objects.create_user(username='test6', password='12345')
        c.login(username='test6', password='12345')
        response = c.post(reverse('edit_schedule'), {'start_day': 'Monday', 'start_time': '10:30',
                                                     'end_day': 'Friday', 'end_time': '10:30'})
        id = Activity.objects.filter(user=user).first().activityId
        response = c.get('/schedule/edit_schedule/' + str(id) + '/remove')
        # response = c.get('/schedule')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Activity.objects.filter(
            user=user, start_day='Monday', end_day='Friday'))

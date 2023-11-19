from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from user.models import UserInfo, Friend
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from user.urls import *
# Create your tests here.


class UserTest(TestCase):
    def setUp(self) -> None:
        user = User.objects.create_user(username='test1', password='12345')

        self.user = User.objects.create(username='testuser')
        self.userInfo = UserInfo.objects.create(
            user_id=self.user, account_UID=123)
        self.friendUserInfo = UserInfo.objects.create(
            user_id=User.objects.create(username='frienduser'), account_UID=456)

        user.save()

    def test_UserProfile_notLogin(self):
        c = Client()
        self.assertRaises(User.DoesNotExist, c.get, '/user/profile/')

    def test_UserProfile_no_UserInfo(self):
        c = Client()
        c.post(reverse('login'), {'username': 'test1', 'pass': '12345'})
        self.assertRaises(UserInfo.DoesNotExist, c.get, '/user/profile/')

    def test_UserProfile_has_UserInfo(self):
        c = Client()
        user = User.objects.create_user(username='test6', password='12345')
        c.post(reverse('login'), {'username': 'test6', 'pass': '12345'})
        UserInfo.objects.create(user_id=user, account_UID=1, age=20,
                                contact="https://www.facebook.com/",
                                gender="Male", phone_number="00")
        response = c.get('/user/profile/')
        self.assertEqual(response.status_code, 200)

    def test_UserInfo_duplicate_UID(self):
        user1 = User.objects.create_user(username='test2', password='12345')
        user2 = User.objects.create_user(username='test3', password='12345')
        UserInfo.objects.create(account_UID=1, user_id=user1, age=20)
        self.assertRaises(IntegrityError, UserInfo.objects.create,
                          account_UID=1, user_id=user2, age=20)

    def test_InValidChangePassword_OldPasswodWrong(self):
        c = Client()
        c.post(reverse('login'), {'username': 'test1', 'pass': '12345'})
        response = c.post(reverse('user:change_password'), {
                          'old_password': '123', 'new_password1': '123456', 'new_password2': '123456'})
        self.assertEqual(response.status_code, 200)

    def test_InValidChangePassword_NewPasswodDontMatch(self):
        c = Client()
        c.post(reverse('login'), {'username': 'test1', 'pass': '12345'})
        response = c.post(reverse('user:change_password'), {
                          'old_password': '12345', 'new_password1': '1', 'new_password2': '12'})
        self.assertEqual(response.status_code, 200)

    def test_InValidChangePassword_NewPasswodEmpty(self):
        c = Client()
        c.post(reverse('login'), {'username': 'test1', 'pass': '12345'})
        response = c.post(reverse('user:change_password'), {
                          'old_password': '12345', 'new_password1': '1', 'new_password2': ''})
        self.assertEqual(response.status_code, 200)

    def test_ValidChangePassword(self):
        c = Client()
        c.post(reverse('login'), {'username': 'test1', 'pass': '12345'})
        response = c.post(reverse('user:change_password'), {
                          'old_password': '12345', 'new_password1': '12345', 'new_password2': '12345'})
        self.assertEqual(response.status_code, 302)

    def test_friend_list_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('user:friend_list', args=(self.userInfo.account_UID,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/friendlist.html')

    def test_friend_list_unauthenticated(self):
        response = self.client.get(
            reverse('user:friend_list', args=(self.userInfo.account_UID,)))
        self.assertRedirects(
            response, f'{reverse("user:signin")}?next=/user/{self.userInfo.account_UID}/friend_list/')

    def test_add_friend(self):
        self.client.force_login(self.user)
        data = {'user_account_UID': self.userInfo.account_UID,
                'friend_account_UID': self.friendUserInfo.account_UID}
        response = self.client.post(reverse('user:add_friend'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/friendlist.html')
        self.assertContains(response, 'Friend added successfully!')

    def test_add_friend_already_friends(self):

        Friend.objects.create(user_id=self.userInfo,
                              friend_id=self.friendUserInfo, status=True)
        Friend.objects.create(user_id=self.friendUserInfo,
                              friend_id=self.userInfo, status=True)

        self.client.force_login(self.user)
        data = {'user_account_UID': self.userInfo.account_UID,
                'friend_account_UID': self.friendUserInfo.account_UID}
        response = self.client.post(reverse('user:add_friend'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/friendlist.html')
        self.assertContains(
            response, f'{self.friendUserInfo.user_id.username} is already a friend of {self.userInfo.user_id.username}')

    def test_add_friend_nonexistent_user(self):
        self.client.force_login(self.user)
        data = {'user_account_UID': self.userInfo.account_UID,
                'friend_account_UID': 999}
        response = self.client.post(reverse('user:add_friend'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/friendlist.html')
        self.assertContains(response, 'User UID not found!')

    def test_edit_profile_view(self):

        self.user = User.objects.create_user(
            username='testuser2', password='testpassword')
        self.client.login(username='testuser2', password='testpassword')
        self.user_info = UserInfo.objects.create(
            user_id=self.user, account_UID=000, sir_name='Test Sir', gender='male', age=25, contact='-')

        # สร้างข้อมูล POST request
        post_data = {
            'username': 'new_username',
            'sir_name': 'New Sir Name',
            'gender': 'Male',
            'age': 30,
            'contact': '-',
        }

        # ทำการ request ไปยัง edit_profile view ด้วยข้อมูล POST
        response = self.client.post(reverse('user:edit_profile'), post_data)

        # ตรวจสอบว่าหน้าถูก redirect ไปที่หน้าหลักหรือไม่
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

        # ทดสอบการแก้ไขข้อมูลโปรไฟล์
        updated_user_info = UserInfo.objects.get(user_id=self.user)

        self.assertEqual(updated_user_info.sir_name, 'New Sir Name')
        self.assertEqual(updated_user_info.gender, 'Male')
        self.assertEqual(updated_user_info.age, 30)
        self.assertEqual(updated_user_info.contact, '-')

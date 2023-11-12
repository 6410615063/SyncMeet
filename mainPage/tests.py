from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

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

    def test_InValidCreateUser_PasswordDontMatch(self):
        c = Client()
        response = c.post(reverse('signup'),{'username':'test2','password1':'12345', 'password2':'123456'})
        self.assertEqual(response.status_code, 200)
    
    def test_InValidCreateUser_MissingUsername(self):
        c = Client()
        response = c.post(reverse('signup'),{'password1':'12345', 'password2':'12345'})
        self.assertEqual(response.status_code, 200)

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
    
    def test_InvalidUserlogin_WrongPassword(self):
        c = Client()
        response = c.post(reverse('login'),{'username':'test1','pass':'123456'})
        self.assertEqual(response.status_code, 200)

    def test_Logout(self):
        c = Client()
        c.post(reverse('login'),{'username':'test5','pass':'12345'})
        response = c.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
    


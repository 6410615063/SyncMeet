from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.test import Client
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist



from .models import Group, GROUP_TAG, Post, POST_TAG
from user.models import UserInfo

# Create your tests here.

# Group Test Case 
class GroupModelTest(TestCase):
    def setUp(self):
        self.creator = User.objects.create_user(username='creator', password='testpassword')
        self.member = User.objects.create_user(username='member', password='testpassword')
        image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        self.group = Group.objects.create(
            gname='Test Group',
            gdescription='Description of the group.',
            gtag='Purple',
            gcreator=self.creator,
            gprofile=image
        )
        self.group.refresh_from_db()
        self.group.gmembers.add(self.member)

    def test_is_creator(self):
        self.assertTrue(self.group.is_creator(self.creator))
        self.assertFalse(self.group.is_creator(self.member))

    def test_str_method(self):
        self.assertEqual(str(self.group), 'Test Group')

    def test_group_tag_choices(self):
        expected_choices = [('Untitled', 'Untitled'), ('Purple', 'Purple'), ('Blue', 'Blue'),
                            ('Green', 'Green'), ('Yellow', 'Yellow'), ('Orange', 'Orange'), ('Red', 'Red')]
        actual_choices = list(GROUP_TAG)
        self.assertEqual(actual_choices, expected_choices)
        for choice in expected_choices:
            self.assertIn(choice, actual_choices)

class GroupViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.admin_user = User.objects.create_user(username='adminuser', password='adminpassword', is_staff=True)
        self.group = Group.objects.create(
            gname='Test Group Name',
            gdescription='Test Group Description',
            gprofile=SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg"),
            gtag='Untitled',
            gcreator=self.user,
        )
        user_info = UserInfo.objects.create(
            user_id=self.user,
            account_UID=123456, 
            profile_image='path/to/profile/image.jpg',
            prefix_phone_number='+66',
            phone_number='123456789',
            sir_name='Test Name',
            gender='testgender',
            age=20,
            contact='https://testcontact.com'
        )
        self.client = Client()

    def test_admin_user_redirect_to_admin_page(self):
        self.client.login(username='adminuser', password='adminpassword')
        response = self.client.get(reverse('group'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('admin:index'))

    def test_authenticated_user_can_view_group(self):
        self.client.login(username='testuser', password='testpassword')
        self.group.gmembers.add(self.user)
        response = self.client.get(reverse('group'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Group')

    def test_unauthenticated_user_cant_view_group(self):
        response = self.client.get(reverse('group'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('group'))

    def test_search_group_by_tag_filter(self):
        self.client.login(username='testuser', password='testpassword')
        self.group.gmembers.add(self.user)
        response = self.client.get(reverse('group') + '?gtag=Untitled')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Group')

class GroupCreateTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')
        user_info = UserInfo.objects.create(
            user_id=self.user,
            account_UID=123456, 
            profile_image='path/to/profile/image.jpg',
            prefix_phone_number='+66',
            phone_number='123456789',
            sir_name='Test Name',
            gender='testgender',
            age=20,
            contact='https://testcontact.com'
        )

    def test_create_group_success(self):
        self.client.login(username='testuser', password='testpassword')
        data = {
            'gname': 'Test Group',
            'gdescription': 'Test Group Description',
            'gtag': 'Blue',
            'gprofile': SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg"),
        }
        response = self.client.post(reverse('create_group'), data, format='multipart')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('group'))
        self.assertTrue(Group.objects.filter(gname='Test Group').exists())

    def test_create_group_fail(self):
        data = {
            'gname': '',  
            'gdescription': 'Test Group Description',
            'gtag': 'Blue',
            'gprofile': SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg"),
        }
        response = self.client.post(reverse('create_group'), data, format='multipart')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Group.objects.filter(gname='Test Group').exists())

class LeaveGroupTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.group = Group.objects.create(
            gname='Test Group Name',
            gdescription='Test Group Description: Lorem ipsum dolor sit amet.',
            gtag='Yellow',
            gcreator=self.user,
        )
        self.group.gmembers.add(self.user)

    def test_leave_group_success(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('leave_group', args=[self.group.id]))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(self.user, self.group.gmembers.all())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You have left the group.")

class GroupMembersTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.group = Group.objects.create(
            gname='Test Group Name',
            gdescription='Test Group Description: Lorem ipsum dolor sit amet.',
            gtag='Red',
            gcreator=self.user,
        )
        user_info = UserInfo.objects.create(
            user_id=self.user,
            account_UID=123456, 
            profile_image='path/to/profile/image.jpg',
            prefix_phone_number='+66',
            phone_number='123456789',
            sir_name='Test Name',
            gender='testgender',
            age=20,
            contact='https://testcontact.com'
        )
        self.group.gmembers.add(self.user)
    
    def test_group_members_view(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('group_members', args=[self.group.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/group_members.html')
        self.assertEqual(response.context['group'], self.group)
        self.assertQuerysetEqual(response.context['members'], self.group.gmembers.all(), transform=lambda x: x)

class EditGroupTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')
        self.group = Group.objects.create(
            gname='Test Group',
            gdescription='This is a test group',
            gtag='Purple',
            gcreator=self.user
        )
    
    def test_edit_group_not_creator(self):
        non_creator_user = User.objects.create_user(username='noncreator', password='testpassword')
        self.client.login(username='noncreator', password='testpassword')
        url = reverse('edit_group', args=[self.group.id])
        data = {
            'gname': 'Updated Group Name',
            'gdescription': 'Updated group description',
            'gtag': 'Blue',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 403)  
        self.group.refresh_from_db()
        self.assertEqual(self.group.gname, 'Test Group')
        self.assertEqual(self.group.gdescription, 'This is a test group')
        
    def test_edit_group_success(self):
        url = reverse('edit_group', args=[self.group.id])
        data = {
            'gname': 'Updated Group Name',
            'gdescription': 'Updated group description',
            'gtag': 'Blue',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        self.group.refresh_from_db()
        self.assertEqual(self.group.gname, 'Updated Group Name')
        self.assertEqual(self.group.gdescription, 'Updated group description')
        self.assertEqual(self.group.gtag, 'Blue')

    def test_edit_group_fail_missing_fields(self):
        url = reverse('edit_group', args=[self.group.id])
        data = {
            'gname': '',  
            'gdescription': '', 
            'gtag': 'Purple',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200) 
        self.group.refresh_from_db()
        self.assertEqual(self.group.gname, 'Test Group')
        self.assertEqual(self.group.gdescription, 'This is a test group')
        self.assertNotContains(response, "Group details have been updated successfully.")

# Post Test Case
class PostViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.group = Group.objects.create(
            gname='Test Group Name',
            gdescription='Test Group Description: Lorem ipsum dolor sit amet.',
            gtag='Untitled',
            gcreator=self.user,
        )
        self.post = Post.objects.create(
            ptitle='Test Post Title',
            pauthor=self.user,
            pcontent='Test Post Description: Lorem ipsum dolor sit amet.',
            ptag='Blue',
            pgroup=self.group,
        )
        user_info = UserInfo.objects.create(
            user_id=self.user,
            account_UID=123456, 
            profile_image='path/to/profile/image.jpg',
            prefix_phone_number='+66',
            phone_number='123456789',
            sir_name='Test Name',
            gender='testgender',
            age=20,
            contact='https://testcontact.com'
        )

    def test_post_view_with_search_by_tag_filter(self):
        self.client.login(username='testuser', password='testpassword')
        tag_filter = 'Blue'
        response = self.client.get(reverse('post', args=[self.group.id]), {'ptag': tag_filter})

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'groups/post.html')
        self.assertEqual(response.context['posts'].count(), 1)
        self.assertEqual(response.context['posts'][0], self.post)
        self.assertEqual(response.context['POST_TAG'], POST_TAG)
        self.assertEqual(response.context['group'], self.group)
        self.assertEqual(response.context['user_info'].user_id, self.user)


    def test_post_view_without_search_by_tag_filter(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('post', args=[self.group.id]))
        self.assertEqual(response.status_code, 200)  
        self.assertTemplateUsed(response, 'groups/post.html')  
        self.assertEqual(response.context['posts'].count(), 1) 
        self.assertEqual(response.context['posts'][0], self.post)  
        self.assertEqual(response.context['POST_TAG'], POST_TAG) 
        self.assertEqual(response.context['group'], self.group) 
        self.assertEqual(response.context['user_info'].user_id, self.user)

class CreatePostTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.group = Group.objects.create(
            gname='Test Group Name',
            gdescription='Test Group Description: Lorem ipsum dolor sit amet.',
            gtag='Purple',
            gcreator=self.user,
        )
        user_info = UserInfo.objects.create(
            user_id=self.user,
            account_UID=123456, 
            profile_image='path/to/profile/image.jpg',
            prefix_phone_number='+66',
            phone_number='123456789',
            sir_name='Test Name',
            gender='testgender',
            age=20,
            contact='https://testcontact.com'
        )
        
    def test_create_post(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.post(reverse('create_post', args=[self.group.id]), {
            'ptitle': 'Test Post Title',
            'pcontent': 'Test Post Description: Lorem ipsum dolor sit amet.',
            'ptag': 'Blue'
        })
        self.assertEqual(response.status_code, 302)  
        self.assertEqual(Post.objects.count(), 1)  
        new_post = Post.objects.first()
        self.assertEqual(new_post.ptitle, 'Test Post Title') 
        self.assertEqual(new_post.pcontent, 'Test Post Description: Lorem ipsum dolor sit amet.')  # Expecting the correct post content
        self.assertEqual(new_post.pauthor, self.user) 
        self.assertEqual(new_post.pgroup, self.group)  
        self.assertEqual(new_post.ptag, 'Blue') 
        self.assertRedirects(response, reverse('post', args=[self.group.id])) 

    def test_create_post_failed(self):
        self.client.login(username='testuser', password='testpassword')

        with self.assertRaises(MultiValueDictKeyError) as context:
            response = self.client.post(reverse('create_post', kwargs={'group_id': self.group.id}), {
                'pcontent': 'Test post content.',
            })
        self.assertEqual(str(context.exception), "'ptitle'")

class DeletePostTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.group = Group.objects.create(
            gname='Test Group Name',
            gdescription='Test Post Description: Lorem ipsum dolor sit amet.',
            gtag='Purple',
            gcreator=self.user,
        )
        self.post = Post.objects.create(
            ptitle='Test Post Title',
            pauthor=self.user,
            pcontent='Test Post Description: Lorem ipsum dolor sit amet.',
            ptag='Blue',
            pgroup=self.group,
        )
        user_info = UserInfo.objects.create(
            user_id=self.user,
            account_UID=123456, 
            profile_image='path/to/profile/image.jpg',
            prefix_phone_number='+66',
            phone_number='123456789',
            sir_name='Test Name',
            gender='testgender',
            age=20,
            contact='https://testcontact.com'
        )

    def test_delete_post_success(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('delete_post', args=[self.group.id]), {'post_id': self.post.id})
        self.assertEqual(response.status_code, 302) 
        self.assertEqual(Post.objects.count(), 0) 
        messages = [m.message for m in get_messages(response.wsgi_request)] 
        self.assertIn("Post deleted successfully.", messages)
        self.assertRedirects(response, reverse('post', args=[self.group.id]))

class EditPostTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.group = Group.objects.create(gname='Test Group', gdescription='This is a test group', gcreator=self.user)
        self.post = Post.objects.create(ptitle='Test Post', pauthor=self.user, pcontent='This is a test post', pgroup=self.group)
        self.non_author_user = User.objects.create_user(username='nonauthor', password='testpassword')
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')

    def test_edit_post_fail_not_author(self):
        self.client.logout()
        self.client.login(username='nonauthor', password='testpassword')
        url = reverse('edit_post', args=[self.group.id, self.post.id])
        data = {
            'ptitle': 'Post Title',
            'pcontent': 'Post content',
            'ptag': 'Green',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 403) 
        self.post.refresh_from_db()
        self.assertEqual(self.post.ptitle, 'Test Post')
        self.assertEqual(self.post.pcontent, 'This is a test post')

    def test_edit_post_success(self):
        url = reverse('edit_post', args=[self.group.id, self.post.id])
        data = {
            'ptitle': 'Updated Post Title',
            'pcontent': 'Updated post content',
            'ptag': 'Blue',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  
        self.post.refresh_from_db()
        self.assertEqual(self.post.ptitle, 'Updated Post Title')
        self.assertEqual(self.post.pcontent, 'Updated post content')
        self.assertEqual(self.post.ptag, 'Blue')
    
    def test_edit_post_fail_missing_fields(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('edit_post', args=[self.group.id, self.post.id]), {
            'ptitle': '', 
            'pcontent': '',  
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "All fields are required.")
        self.post.refresh_from_db()
        self.assertNotEqual(self.post.ptitle, '')
        self.assertNotEqual(self.post.pcontent, '')




# ERROR TEST
class AddMemberTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.group = Group.objects.create(
            gname='Test Group Name',
            gdescription='Test Group Description',
            gtag='Test Tag',
            gcreator=self.user,
        )

    def test_add_member_success(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('add_member', args=[self.group.id]), {'account_UID': self.user.id})

        self.assertRedirects(response, reverse('group_members', args=[self.group.id]))
        self.assertIn(self.user, self.group.gmembers.all())

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f"User {self.user.username} has been added to the group.")

    def test_add_member_nonexistent_user(self):
        self.client.login(username='testuser', password='testpassword')
        non_existent_user_id = self.user.id + 100
        response = self.client.post(reverse('add_member', args=[self.group.id]), {'account_UID': non_existent_user_id})
        self.assertTemplateUsed(response, 'groups/add_member.html')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f"User with ID {non_existent_user_id} does not exist.")
        self.assertNotIn(self.user, self.group.gmembers.all())


class RemoveMemberTestCase(TestCase):
    def setUp(self):
        
        self.user_creator = User.objects.create_user(username='creator', password='testpassword')
        # สร้างกลุ่มและสมาชิก
        self.group = Group.objects.create(
            gname='Test Group',
            gdescription='Test Group Description',
            gtag='Test Tag',
            gcreator=self.user_creator,
        )
        self.user_member = User.objects.create_user(username='member', password='testpassword')
        self.group.gmembers.add(self.user_member)

    def test_remove_member_success(self):
        response = self.client.post(reverse('remove_member', args=[self.group.id]), {'selected_members': [self.user_member.id]})
        self.assertEqual(response.status_code, 200)

        storage = get_messages(response.wsgi_request)
        messages = [msg.message for msg in storage]
        self.assertIn('Selected members have been removed.', messages)

        self.assertNotIn(self.user_member, self.group.gmembers.all())

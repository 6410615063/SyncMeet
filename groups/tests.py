from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist



from .models import Group, GROUP_TAG, Post, POST_TAG

# Create your tests here.

# Group Test Case 
class GroupViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.group = Group.objects.create(
            gname='Test Group Name',
            gdescription='Test Group Description: Lorem ipsum dolor sit amet.',
            gtag='Untitled',
            gcreator=self.user,
        )
        self.group.gmembers.add(self.user)

    def test_group_view_authenticated_user(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(reverse('group'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups/group.html')
        self.assertEqual(response.context['groups'].count(), 1)
        self.assertEqual(response.context['groups'][0], self.group)
        self.assertEqual(response.context['GROUP_TAG'], GROUP_TAG)

    def test_group_view_authenticated_user_no_groups(self):
        self.group.gmembers.remove(self.user)

        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(reverse('group'))

        self.assertEqual(response.status_code, 200) 
        self.assertTemplateUsed(response, 'groups/group.html')  
        self.assertEqual(response.context['groups'].count(), 0) 
        self.assertEqual(response.context['GROUP_TAG'], GROUP_TAG)
    
    def test_group_view_not_authenticated_user(self):
        response = self.client.get(reverse('group'))

        self.assertEqual(response.status_code, 302)

    def test_group_view_admin_user(self):
        admin_user = User.objects.create_superuser(username='adminuser', password='testpassword', email='admin@example.com')
        self.client.login(username='adminuser', password='testpassword')

        response = self.client.get(reverse('group'))

class GroupCreateTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_create_group_success(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.post(reverse('create_group'), {
            'gname': 'Test Group Name',
            'gdescription': 'Test Group Description: Lorem ipsum dolor sit amet.',
            'gtag': 'Purple',
            'gprofile': SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg"),
        })

        self.assertEqual(response.status_code, 302)

        self.assertEqual(Group.objects.count(), 1)
        new_group = Group.objects.first()

        self.assertEqual(new_group.gname, 'Test Group Name')
        self.assertEqual(new_group.gdescription, 'Test Group Description: Lorem ipsum dolor sit amet.')
        self.assertEqual(new_group.gtag, 'Purple')
        self.assertEqual(new_group.gcreator, self.user)

        self.assertEqual(new_group.gmembers.count(), 1)

    def test_create_group_failed(self):
        self.client.login(username='testuser', password='testpassword')

        with self.assertRaises(MultiValueDictKeyError) as context:
            response = self.client.post(reverse('create_group'), {
                'gdescription': 'Test group description',
                'gtag': 'Purple',
                'gprofile': 'path/to/profile.jpg',
            })

        self.assertEqual(str(context.exception), "'gname'")

class LeaveGroupTestCase(TestCase):
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


class GroupMembersTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.group = Group.objects.create(
            gname='Test Group Name',
            gdescription='Test Group Description: Lorem ipsum dolor sit amet.',
            gtag='Red',
            gcreator=self.user,
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


# Post Test Case
class PostViewTestCase(TestCase):
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

    def test_post_view_with_search_by_tag_filter(self):
        response = self.client.get(reverse('post', args=[self.group.id]), {'ptag': 'Blue'})

        self.assertEqual(response.status_code, 200) 
        self.assertTemplateUsed(response, 'groups/post.html')  
        self.assertEqual(response.context['posts'].count(), 1)  
        self.assertEqual(response.context['posts'][0], self.post) 
        self.assertEqual(response.context['POST_TAG'], POST_TAG)  
        self.assertEqual(response.context['group'], self.group)

    def test_post_view_without_search_by_tag_filter(self):
        response = self.client.get(reverse('post', args=[self.group.id]))

        self.assertEqual(response.status_code, 200)  
        self.assertTemplateUsed(response, 'groups/post.html')  
        self.assertEqual(response.context['posts'].count(), 1) 
        self.assertEqual(response.context['posts'][0], self.post)  
        self.assertEqual(response.context['POST_TAG'], POST_TAG) 
        self.assertEqual(response.context['group'], self.group) 


class CreatePostTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.group = Group.objects.create(
            gname='Test Group Name',
            gdescription='Test Group Description: Lorem ipsum dolor sit amet.',
            gtag='Purple',
            gcreator=self.user,
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

class DeletePostTestCase(TestCase):
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
    
    def test_delete_post_success(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.post(reverse('delete_post', args=[self.group.id]), {'post_id': self.post.id})

        self.assertEqual(response.status_code, 302) 
        self.assertEqual(Post.objects.count(), 0) 
        messages = [m.message for m in get_messages(response.wsgi_request)] 
        self.assertIn("Post deleted successfully.", messages)
        self.assertRedirects(response, reverse('post', args=[self.group.id]))
        


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
        self.assertEqual(response.status_code, 302)

        storage = get_messages(response.wsgi_request)
        messages = [msg.message for msg in storage]
        self.assertIn('Selected members have been removed.', messages)

        self.assertNotIn(self.user_member, self.group.gmembers.all())


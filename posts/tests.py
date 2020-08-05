from django.test import TestCase, Client

from posts.models import User, Post, Group


class TestPosts(TestCase):
    def setUp(self):
        self.login_client = Client()
        self.logout_client = Client()
        self.user = User.objects.create_user(username="test", password="testpassword12345", email="test@yandex.ru")
        self.login_client.force_login(self.user)
        self.logout_client.logout()
        self.group = Group.objects.create(title='testgroup', slug='testgroup')
        self.post = Post.objects.create(text='Test post', author=self.user, group=self.group)  # Check if authorized user can create a post

    def test_new_post(self):
        response_index = self.login_client.get("")
        self.assertIn(self.post.text, str(response_index.content))  # Check if new post added to /index/ page

        response_profile = self.login_client.get(f"/{self.user}/")
        self.assertIn(self.post.text, str(response_profile.content))  # Check if new post added to /profile/page

        response_edit = self.login_client.get(f"/{self.user}/{self.post.id}/")
        self.assertIn(self.post.text, str(response_edit.content))  # Check if new post added to /profile/post_id page

    def test_edit_post(self):
        self.post = Post.objects.get(id=self.post.id)
        self.post.text = 'Test post after update'
        self.post.save()

        response_index = self.login_client.get("")
        self.assertIn('Test post after update', str(response_index.content))  # Check if post was edited on /index/ page

        response_profile = self.login_client.get(f"/{self.user}/")
        self.assertIn('Test post after update', str(response_profile.content))  # Check if post was edited on /profile/ page

        response_edit = self.login_client.get(f"/{self.user}/{self.post.id}/")
        self.assertIn('Test post after update', str(response_edit.content))  # Check if post was edited on /profile/post_id page

        response_group = self.login_client.get(f"/group/{self.group}/")
        self.assertIn('Test post after update', str(response_group.content))  # Check if post was edited on /group/ page_number

    def test_unauthorized(self):
        response = self.logout_client.post('/new/', {'text': 'Test post', 'author': 'anonymous'})
        self.assertEqual(response['location'], '/auth/login/?next=/new/')  # Check if redirect goes to login page
        self.assertEqual(response.status_code, 302)  # Check if unauthorized user redirects when trying to use /new/ page


class TestProfile(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test", password="testpassword12345", email="test@yandex.ru")

    def test_profile(self):
        response = self.client.get(f"/{self.user}/")
        self.assertEqual(response.status_code, 200)  # Check if new user profile page exists

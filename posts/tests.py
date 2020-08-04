from django.test import TestCase, Client

from posts.models import User, Post


class TestStringMethods(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test", password="testpassword12345", email="test@yandex.ru")
        self.client.login(username='test', password='testpassword12345')
        self.post = Post.objects.create(text='Test post', author=self.user)  # Check if authorized user can create a post

    def test_profile(self):
        response = self.client.get(f"/{self.user}/")
        self.assertEqual(response.status_code, 200)  # Check if new user profile page exists

    def test_new_post(self):
        response_index = self.client.get("")
        self.assertIn(self.post.text, str(response_index.content))  # Check if new post added to /index/ page

        response_profile = self.client.get(f"/{self.user}/")
        self.assertIn(self.post.text, str(response_profile.content))  # Check if new post added to /profile/page

        response_edit = self.client.get(f"/{self.user}/{self.post.id}/")
        self.assertIn(self.post.text, str(response_edit.content))  # Check if new post added to /profile/post_id page

    def test_edit_post(self):
        self.post = Post.objects.get(id=self.post.id)
        self.post.text = 'Test post after update'
        self.post.save()
        response_edit = self.client.get(f"/{self.user}/{self.post.id}/")
        self.assertIn('Test post after update', str(response_edit.content))  # Check if post was edited from authorized user

    def test_unauthorized(self):
        self.client.logout()
        response = self.client.get("/new/")
        self.assertEqual(response['location'], '/auth/login/?next=/new/')  # Check if redirect goes to login page
        self.assertEqual(response.status_code, 302)  # Check if unauthorized user redirects when trying to use /new/ page

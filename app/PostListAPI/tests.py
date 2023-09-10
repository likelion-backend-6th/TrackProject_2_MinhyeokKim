from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory

from PostListAPI.models import Post, Follow
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponse


class PostFollowTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = APIRequestFactory()
        cls.superuser = User.objects.create_superuser(
            username="superuser",
            email=None,
            password=None,
        )
        for i in range(5):
            user = User.objects.create_user(
                username=f"testuser {i+1}",
                email=None,
                password=None,
            )
            for j in range(3):
                Post.objects.create(
                    author=user,
                    title=f"Test Post {j} by User {i}",
                    content=f"Content of Post {j} by User {i}",
                )
        users = User.objects.all()
        for i in range(len(users) - 1):
            follower = users[i]
            following = users[i + 1]
            Follow.objects.create(follower=follower, following=following)

    def test_get_all_posts(self):
        user = User.objects.get(username="superuser")
        self.client.force_authenticate(user=user)
        response = self.client.get(reverse("post-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

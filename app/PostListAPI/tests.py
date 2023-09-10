from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory

from PostListAPI.models import Post, Follow
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponse
from random import choice


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
        for user in users:
            print(user.username)

        for i in range(len(users) - 1):
            follower = users[i]
            following = users[i + 1]
            Follow.objects.create(follower=follower, following=following)

        follows = Follow.objects.all()
        for follow in follows:
            print(
                f"{follow.follower.username} is following {follow.following.username}"
            )

    def test_get_all_users_except_itself(self):
        random_user = User.objects.order_by("?").first()
        self.client.force_authenticate(user=random_user)
        response = self.client.get(reverse("user-all_users"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_user_ids = [user["id"] for user in response.data]

        self.assertNotIn(random_user.id, returned_user_ids)

    def test_get_all_posts(self):
        random_user = User.objects.order_by("?").first()
        self.client.force_authenticate(user=random_user)
        response = self.client.get(reverse("post-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_own_post(self):
        random_user = User.objects.order_by("?").first()
        self.client.force_authenticate(user=random_user)
        random_post = Post.objects.filter(author=random_user).order_by("?").first()

        if random_post is None:
            self.fail("No post found")

        url = reverse("post-detail", kwargs={"pk": random_post.id})

        update_data = {
            "title": "Updated Title",
            "content": "Updated Content",
        }

        response = self.client.put(url, data=update_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Title")
        self.assertEqual(response.data["content"], "Updated Content")

    def test_delete_own_post(self):
        random_user = User.objects.order_by("?").first()
        self.client.force_authenticate(user=random_user)

        random_post = Post.objects.filter(author=random_user).order_by("?").first()

        if random_post is None:
            self.fail("No post found")

        url = reverse("post-detail", kwargs={"pk": random_post.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_add_follow(self):
        random_user = User.objects.order_by("?").first()
        self.client.force_authenticate(user=random_user)

        all_users_response = self.client.get(reverse("user-all_users"))
        all_users = all_users_response.data

        followed_users = Follow.objects.filter(follower=random_user).values_list(
            "following", flat=True
        )

        non_followed_users = []
        for user in all_users:
            if user["id"] not in followed_users and user["id"] != random_user.id:
                non_followed_users.append(user)

        random_user_to_follow = choice(non_followed_users)

        url = reverse("follow-add_follow")
        data = {"following_id": random_user_to_follow["id"]}

        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Follow.objects.filter(
                follower=random_user, following__id=random_user_to_follow["id"]
            ).exists()
        )

    def test_unfollow(self):
        users_with_follows = set()  # delete duplication
        for follow_instance in Follow.objects.all():
            users_with_follows.add(follow_instance.follower)

        users_with_follows = list(users_with_follows)

        random_user = choice(users_with_follows)
        self.client.force_authenticate(user=random_user)

        followed_users = Follow.objects.filter(follower=random_user).values_list(
            "following", flat=True
        )

        try:
            random_user_to_unfollow = choice(followed_users)
        except IndexError:
            self.fail("No users to unfollow")

        url = reverse(
            "follow-unfollow", kwargs={"following_id": random_user_to_unfollow}
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            Follow.objects.filter(
                follower=random_user, following__id=random_user_to_unfollow
            ).exists()
        )

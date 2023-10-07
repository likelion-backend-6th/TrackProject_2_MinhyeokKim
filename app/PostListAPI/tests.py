from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from PostListAPI.models import Post, Follow
from random import choice


class PostFollowTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        for i in range(3):
            user = User.objects.create_user(username=f"user{i}")
            setattr(cls, f"user{i}", user)
            for j in range(3):
                post = Post.objects.create(
                    user=user,
                    content=f"{user}'s Content{j}",
                )
                setattr(cls, f"{user}_post{j}", post)

    def test_get_all_users_except_itself(self):
        # login a random use
        random_user = User.objects.order_by("?").first()
        self.client.force_authenticate(user=random_user)
        # get all users except itself
        response = self.client.get(reverse("user-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # check if the user is in the response
        returned_user_ids = [user["id"] for user in response.data]
        self.assertNotIn(random_user.id, returned_user_ids)

    def test_get_all_posts(self):
        random_user = User.objects.order_by("?").first()
        self.client.force_authenticate(user=random_user)
        response = self.client.get(reverse("post-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 9)

    def test_get_mine_posts(self):
        random_user = User.objects.order_by("?").first()
        self.client.force_authenticate(user=random_user)
        url = reverse("post-list")
        response = self.client.get(f"{url}?mine=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        for post in response.data:
            self.assertEqual(post["user"], random_user.id)

    def test_update_own_post(self):
        users_with_posts = User.objects.filter(post__isnull=False).distinct()

        if not users_with_posts.exists():
            self.fail("No users with posts: setup data error")

        random_user = users_with_posts.order_by("?").first()

        self.client.force_authenticate(user=random_user)
        random_post = Post.objects.filter(user=random_user).order_by("?").first()

        url = reverse("post-detail", kwargs={"pk": random_post.id})

        update_data = {
            "content": "Updated Content",
        }

        response = self.client.patch(url, data=update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["content"], "Updated Content")

        # if a stranger tries to update the post, it should fail
        stranger = users_with_posts.exclude(id=random_user.id).order_by("?").first()
        self.client.force_authenticate(user=stranger)
        response = self.client.patch(url, data=update_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_own_post(self):
        users_with_posts = User.objects.filter(post__isnull=False).distinct()

        if not users_with_posts.exists():
            self.fail("No users with posts: setup data error")

        random_user = users_with_posts.order_by("?").first()
        stranger = users_with_posts.exclude(id=random_user.id).order_by("?").first()
        random_post = Post.objects.filter(user=random_user).order_by("?").first()
        url = reverse("post-detail", kwargs={"pk": random_post.id})

        # if stranger tries to delete the post, it should fail
        self.client.force_authenticate(user=stranger)
        response = self.client.delete(url)  # create request based on above data
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # if the user tries to delete the post, it should succeed
        self.client.force_authenticate(user=random_user)
        response = self.client.delete(url)  # create request based on above data
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=random_post.id).exists())

    def test_follow_unfollow(self):
        random_user = User.objects.order_by("?").first()
        stranger = User.objects.exclude(id=random_user.id).order_by("?").first()
        self.client.force_authenticate(user=random_user)
        url = reverse("follow")

        # follow
        response = self.client.post(url, {"following": stranger.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Follow.objects.filter(follower=random_user, following=stranger).exists()
        )

        # unfollow
        response = self.client.post(url, {"following": stranger.id})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Follow.objects.filter(follower=random_user, following=stranger).exists()
        )

    def test_get_following_posts(self):
        random_user = User.objects.order_by("?").first()
        folloing_user = User.objects.exclude(id=random_user.id).order_by("?").first()
        Follow.objects.create(follower=random_user, following=folloing_user)

        self.client.force_authenticate(user=random_user)
        url = reverse("feed")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

from rest_framework.routers import DefaultRouter
from PostListAPI.views import PostViewSet, FollowViewSet


# Create a router and register our viewsets with it.
router = DefaultRouter()

router.register("posts", PostViewSet, basename="post")
router.register("follows", FollowViewSet, basename="follow")

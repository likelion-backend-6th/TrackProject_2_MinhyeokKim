from rest_framework.routers import DefaultRouter
from PostListAPI.views import PostViewSet, FollowViewSet


# Create a router and register our viewsets with it.
router = DefaultRouter()

router.register("post", PostViewSet, basename="post")
router.register("follow", FollowViewSet, basename="follow")

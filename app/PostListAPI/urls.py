from django.urls import path

from rest_framework.routers import DefaultRouter
from PostListAPI.views import PostViewSet, FollowView, UserViewSet, FeedView


# Create a router and register our viewsets with it.
router = DefaultRouter()

router.register(r"post", PostViewSet)
router.register(r"user", UserViewSet)

urlpatterns = [
    path("follow/", FollowView.as_view(), name="follow"),
    path("feed/", FeedView.as_view(), name="feed"),
] + router.urls

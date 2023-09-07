from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status, permissions

from PostListAPI.models import Post, Follow
from PostListAPI.serializers import PostSerializer, FollowSerializer


# Post CRUD
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


# Follow CRUD
class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer

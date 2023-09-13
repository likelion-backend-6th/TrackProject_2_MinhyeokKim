from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status, views
from rest_framework.exceptions import PermissionDenied

from PostListAPI.models import Post, Follow
from django.contrib.auth.models import User
from PostListAPI.serializers import PostSerializer, FollowSerializer, UserSerializer


# User R
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        if self.action == "list":
            return User.objects.exclude(id=self.request.user.id)
        return super().get_queryset()


# Post CRUD
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def check_authentication(self, request):
        if request.user != self.get_object().user:
            raise PermissionDenied("You do not have permission to perform this action.")

    def get_queryset(self):
        mine = self.request.query_params.get("mine", None)

        if mine:
            return Post.objects.filter(user_id=self.request.user.id).order_by(
                "-created_date"
            )
        else:
            return Post.objects.all().order_by("-created_date")

    def update(self, request, *args, **kwargs):
        self.check_authentication(request)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self.check_authentication(request)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.check_authentication(request)
        return super().destroy(request, *args, **kwargs)


# Follow CRUD
class FollowView(views.APIView):
    def post(self, request, format=None):
        serializer = FollowSerializer(data=request.data)

        if serializer.is_valid():
            following = serializer.validated_data["following"]
            qs = Follow.objects.filter(follower=request.user, following=following)

            if qs.exists():  # delete if it already exists.
                qs.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:  # follow if it does not
                Follow.objects.create(
                    follower=request.user,
                    following=following,
                )
                return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FeedView(views.APIView):
    def get(self, request, format=None):
        user = request.user
        following_ids = Follow.objects.filter(follower=user).values_list(
            "following", flat=True
        )

        posts = Post.objects.filter(user__in=following_ids)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

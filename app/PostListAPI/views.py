import uuid
import boto3

from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import viewsets, status, views
from rest_framework.exceptions import PermissionDenied

from PostListAPI.models import Post, Follow
from django.contrib.auth.models import User
from django.core.files.base import File
from django.conf import settings
from django.db.models import Case, When, Value, BooleanField
from PostListAPI.serializers import (
    PostSerializer,
    FollowSerializer,
    UserSerializer,
    PostUploadSerializer,
)


# User R
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # update context to find out who's following data must be returned
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_queryset(self):
        if self.action == "list":
            # get following ids
            following_ids = Follow.objects.filter(
                follower=self.request.user
            ).values_list("following", flat=True)

            # folloing users at the top of the list
            user_queryset = (
                User.objects.exclude(id=self.request.user.id)
                .annotate(
                    is_following=Case(
                        When(id__in=following_ids, then=Value(True)),
                        default=Value(False),
                        output_field=BooleanField(),
                    )
                )
                .order_by("-is_following", "id")
            )
            return user_queryset
        return super().get_queryset()


# Post CRUD
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return PostUploadSerializer
        return super().get_serializer_class()

    def check_authentication(self, request):
        if request.user != self.get_object().user:
            raise PermissionDenied("You do not have permission to perform this action.")

    @extend_schema(deprecated=True)
    def list(self, request, *args, **kwargs):
        return Response(status=status.HTTP_400_BAD_REQUEST, data="Deprecated API")

    def image_handler(self, request: Request, existing_post=None):
        image_url = existing_post.image_url if existing_post else None

        # ":=" : if right side does exists, define left
        if image := request.data.get("image"):
            image: File
            endpoint_url = "https://kr.object.ncloudstorage.com"
            access_key = settings.NCP_ACCESS_KEY
            secret_key = settings.NCP_SECRET_KEY
            bucket_name = "sns-app"

            s3 = boto3.client(
                "s3",
                endpoint_url=endpoint_url,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
            )
            image_id = str(uuid.uuid4())
            file_extension = image.name.split(".")[-1]
            image_name = f"{image_id}.{file_extension}"

            s3.upload_fileobj(image.file, bucket_name, image_name)
            # There is a change to cause security issue if url is being used itself (not recommended)
            # so that, uuid has been used intead
            s3.put_object_acl(
                ACL="public-read",
                Bucket=bucket_name,
                Key=image_name,
            )
            image_url = f"{endpoint_url}/{bucket_name}/{image_name}"
        return image_url

    def get_queryset(self):
        # post/?mine=true
        mine = self.request.query_params.get("mine", None)
        # post/?mine=true&only_hidden=true
        only_hidden = self.request.query_params.get("only_hidden", None)

        if mine:
            if only_hidden:
                return Post.objects.filter(
                    user_id=self.request.user.id, is_hidden=True
                ).order_by("-created_date")
            else:
                return Post.objects.filter(user_id=self.request.user.id).order_by(
                    "-created_date"
                )
        else:
            return Post.objects.filter(is_hidden=False).order_by("-created_date")

    def create(self, request: Request, *args, **kwargs):
        # image_url data check and define
        image_url = self.image_handler(request)

        # Check if the data from client meets the defined rules
        serializer = PostSerializer(data=request.data)
        # serializer = PostSerializer(data=request.data)

        if serializer.is_valid():  # if so,
            data = serializer.validated_data
            data["user"] = request.user
            data["image_url"] = image_url if request.data.get("image") else None
            response: Post = serializer.create(data)  # save to DB
            return Response(
                data=PostSerializer(response).data, status=status.HTTP_201_CREATED
            )
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        self.check_authentication(request)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self.check_authentication(request)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.check_authentication(request)
        return super().destroy(request, *args, **kwargs)

    def toggle_hidden(self, request, pk=None):
        self.check_authentication(request)
        post = self.get_object()
        post.is_hidden = not post.is_hidden
        post.save()


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

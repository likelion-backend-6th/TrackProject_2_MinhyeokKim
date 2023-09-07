from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from PostListAPI.urls import router as post_list_api_router


urlpatterns = [
    path("admin/", admin.site.urls),
    path("post/", include(post_list_api_router.urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

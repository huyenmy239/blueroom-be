from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, NoteViewSet


router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'notes', NoteViewSet)


urlpatterns = [
    path('', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
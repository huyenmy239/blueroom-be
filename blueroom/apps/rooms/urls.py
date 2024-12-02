from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'subjects', views.SubjectViewSet)
router.register(r'backgrounds', views.BackgroundViewSet)
router.register(r'room', views.RoomViewSet)
router.register(r'admin/reports', views.ReportViewSet, basename="reports")

urlpatterns = [
    path('', include(router.urls)),
]


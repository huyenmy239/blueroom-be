from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'subjects', views.SubjectViewSet)
router.register(r'backgrounds', views.BackgroundViewSet)
router.register(r'room', views.RoomViewSet)
router.register(r'admin/reports', views.ReportViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
    path('<int:room_id>/mic/', views.ToggleMicView.as_view(), name='toggle_mic'),
    path('<int:room_id>/block/', views.BlockUserView.as_view(), name='block_user'),
]


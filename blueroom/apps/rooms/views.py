from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Subject, Background
from .serializers import SubjectSerializer, BackgroundSerializer
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

@permission_classes([AllowAny])
class BackgroundViewSet(viewsets.ModelViewSet):
    queryset = Background.objects.all()
    serializer_class = BackgroundSerializer

    # Override destroy method để tùy chỉnh phản hồi khi xóa
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({"message": "Background has been deleted"}, status=status.HTTP_204_NO_CONTENT)

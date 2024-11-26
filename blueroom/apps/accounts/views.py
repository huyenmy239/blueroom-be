from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.authtoken.models import Token
from datetime import timedelta
from django.utils.timezone import now
from .models import User
from .serializers import UserSerializer, LoginSerializer, UpdatePasswordSerializer
from apps.rooms.models import Participation

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['register', 'login']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        validated_data['is_busy'] = False
        validated_data['is_user'] = True
        validated_data['password'] = make_password(validated_data['password'])

        user = serializer.save(**validated_data)
        return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "username": user.username,
                "email": user.email,
                "role": "User" if user.is_user else "Admin"
            }, status=200)

        return Response({"error": "Invalid username or password"}, status=401)

    @action(detail=False, methods=['get'], url_path='profile')
    def profile(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['put'], url_path='profile/update')
    def update_profile(self, request):
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Xử lý ảnh tải lên
        avatar = request.FILES.get('profile_picture')  # Lấy tệp ảnh từ request
        if avatar:
            user.avatar = avatar
        serializer.save()

        return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'], url_path='change-password')
    def change_password(self, request):
        serializer = UpdatePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({"error": "Old password is incorrect"}, status=400)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({"message": "Password changed successfully"}, status=200)

    @action(detail=False, methods=['get'], url_path='history')
    def history(self, request):
        user = request.user
        last_24_hours = now() - timedelta(hours=24)

        participations = Participation.objects.filter(user_id=user, time_in__gte=last_24_hours)
        history = [
            {
                "room_id": participation.room_id.id,
                "room_title": participation.room_id.title,
                "time_in": participation.time_in,
                "time_out": participation.time_out,
            }
            for participation in participations
        ]
        return Response(history, status=200)

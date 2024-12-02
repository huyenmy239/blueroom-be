from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Permission class để kiểm tra xem người dùng có phải là admin (is_user=False) hay không.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and not request.user.is_user

class IsRoomOwner(permissions.BasePermission):
    """
    Permission class cho phép chỉ chủ phòng mới có thể thực hiện thao tác khóa/mở khóa phòng.
    """
    
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user
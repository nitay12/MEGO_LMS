from django.contrib.auth import get_user_model
from rest_framework import permissions

CustomUser = get_user_model()


# User permissions
class IsAdminOrUserOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        else:
            return request.user.is_authenticated and request.user.is_admin

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin or request.user.email == obj.email:
            return True
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return False


# Course permissions
class IsAdminOrCourseOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        else:
            return request.user.is_authenticated and request.user.is_admin

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.classrooms.filter(users=request.user).exists()
        if request.user.is_admin:
            return True
        return False


# Classroom permissions
class IsAdminOrClassroomOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        else:
            return request.user.is_authenticated and request.user.is_admin

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.users.filter(email=request.user.email).exists()
        if request.user.is_admin:
            return True
        return False


# Assignment permissions
class IsAdminOrExaminer(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        else:
            return request.user.is_authenticated and (request.user.is_admin or request.user.is_staff)


class IsAdminOrExaminerOrAssignmentOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        else:
            return request.user.is_authenticated and (request.user.is_admin or request.user.is_staff)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.course.classrooms.filter(users=request.user).exists()
        if request.user.is_admin or request.user.is_staff:
            return True
        return False

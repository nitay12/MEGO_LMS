from django.contrib.auth import get_user_model
from rest_framework import permissions

from assignments.models import Assignment

CustomUser = get_user_model()


# User permissions
class IsActivatedAccount(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.activated_account


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


class IsAdminOrExaminerOrSubmissionOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_admin or request.user.is_staff:
            return True
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        if request.method == 'POST':
            assignment_id = request.data.get('assignment')
            if assignment_id:
                try:
                    return Assignment.objects.filter(course__classrooms__users=request.user, id=assignment_id).exists()
                except Assignment.DoesNotExist:
                    return False
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin or request.user.is_staff:
            return True
        if request.method in permissions.SAFE_METHODS or request.method in ['PUT', 'PATCH', 'DESTROY']:
            return obj.user == request.user
        if request.user.is_admin or request.user.is_staff:
            return True
        return False

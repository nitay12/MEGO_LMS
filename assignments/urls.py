from django.urls import path

from .views import (
    UserListCreateView, UserDetailView,
    CourseListCreateView, CourseDetailView, CourseAssignmentsListView,
    ClassroomListCreateView, ClassroomDetailView,
    AssignmentListCreateView, AssignmentDetailView, AssignmentSubmissionsListView,
    SubmissionListCreateView, SubmissionDetailView,
)

urlpatterns = [
    # Users
    path('users/', UserListCreateView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),

    # Courses
    path('courses/', CourseListCreateView.as_view(), name='course-list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('courses/<int:id>/assignments/', CourseAssignmentsListView.as_view(), name='course-detail'),

    # Course Assignments
    path('courses/<int:course_id>/assignments/', AssignmentListCreateView.as_view(), name='assignment-list'),

    # Classrooms
    path('classrooms/', ClassroomListCreateView.as_view(), name='classroom-list'),
    path('classrooms/<int:pk>/', ClassroomDetailView.as_view(), name='classroom-detail'),

    # Assignments
    path('assignments/', AssignmentListCreateView.as_view(), name='assignment-list-all'),
    path('assignments/<int:pk>/', AssignmentDetailView.as_view(), name='assignment-detail'),

    # Assignment Submissions
    path('assignments/<int:id>/submissions/', AssignmentSubmissionsListView.as_view(),
         name='submission-list-assignment'),

    # Submissions
    path('submissions/', SubmissionListCreateView.as_view(), name='submission-list-all'),
    path('submissions/<int:pk>/', SubmissionDetailView.as_view(), name='submission-detail'),
]

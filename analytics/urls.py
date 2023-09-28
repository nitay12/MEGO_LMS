from django.urls import path
from .views import AssignmentAnalyticsView, StudentAnalyticsView, ClassroomAnalyticsView

urlpatterns = [
    path('assignments/<int:assignment_id>/analytics/', AssignmentAnalyticsView.as_view(), name='assignment-analytics'),
    path('users/<int:student_id>/analytics/', StudentAnalyticsView.as_view(), name='user-analytics'),
    path('classrooms/<int:classroom_id>/analytics/', ClassroomAnalyticsView.as_view(), name='classroom-analytics'),
]

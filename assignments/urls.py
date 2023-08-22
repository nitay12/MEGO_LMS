from django.urls import path
from .views import ClassroomListCreateView, CourseListCreateView, AssignmentListCreateView, SubmissionListCreateView

app_name = 'assignments'

urlpatterns = [
    path('classrooms/', ClassroomListCreateView.as_view(), name='classroom-list-create'),
    path('courses/', CourseListCreateView.as_view(), name='course-list-create'),
    path('assignments/', AssignmentListCreateView.as_view(), name='assignment-list-create'),
    path('submissions/', SubmissionListCreateView.as_view(), name='submission-list-create'),
]

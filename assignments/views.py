from rest_framework import generics
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Course, Classroom, Assignment, Submission, CustomUser
from .permissions import IsAdminOrCourseOwner, IsAdminOrUserOwner, IsAdminOrClassroomOwner, IsAdminOrExaminer, \
    IsAdminOrExaminerOrAssignmentOwner
from .serializers import CourseSerializer, ClassroomSerializer, AssignmentSerializer, SubmissionSerializer, \
    CustomUserSerializer


class UserListCreateView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdminOrUserOwner]
    authentication_classes = [JWTAuthentication]


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdminOrUserOwner]
    authentication_classes = [JWTAuthentication]


class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrCourseOwner]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        if self.request.user.is_admin:
            return Course.objects.all()
        else:
            return Course.objects.filter(classrooms__users=self.request.user)


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrCourseOwner]
    authentication_classes = [JWTAuthentication]


class ClassroomListCreateView(generics.ListCreateAPIView):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    permission_classes = [IsAdminOrClassroomOwner]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        if self.request.user.is_admin:
            return Classroom.objects.all()
        else:
            return Classroom.objects.filter(users=self.request.user)


class ClassroomDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    permission_classes = [IsAdminOrClassroomOwner]
    authentication_classes = [JWTAuthentication]


class AssignmentListCreateView(generics.ListCreateAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAdminOrExaminer]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        if self.request.user.is_admin or self.request.user.is_staff:
            return Assignment.objects.all()
        else:
            return Assignment.objects.filter(course__classrooms__users=self.request.user)


class AssignmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAdminOrExaminerOrAssignmentOwner]
    authentication_classes = [JWTAuthentication]


class SubmissionListCreateView(generics.ListCreateAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer


class SubmissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer

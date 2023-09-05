from django.utils import timezone
from rest_framework import generics
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Course, Classroom, Assignment, Submission, CustomUser
from .permissions import IsAdminOrCourseOwner, IsAdminOrUserOwner, IsAdminOrClassroomOwner, \
    IsAdminOrExaminerOrAssignmentOwner, IsAdminOrExaminerOrSubmissionOwner
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


class CourseAssignmentsListView(generics.ListAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [IsAdminOrCourseOwner]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        # Get the course_id from the URL parameter
        course_id = self.kwargs.get('id')
        is_course_owner = Course.objects.filter(classrooms__users=self.request.user, id=course_id).exists()
        print(is_course_owner)
        if self.request.user.is_admin or self.request.user.is_staff or is_course_owner:
            return Assignment.objects.filter(course_id=course_id)
        else:
            raise PermissionDenied({"error": "you are not signed to this course"})


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
    permission_classes = []
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


class AssignmentSubmissionsListView(generics.ListAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [IsAdminOrExaminerOrSubmissionOwner]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        # Get the Assignment_id from the URL parameter
        assignment_id = self.kwargs.get('id')
        is_assignment_owner = Assignment.objects.filter(course__classrooms__users=self.request.user,
                                                        id=assignment_id).exists()
        print(assignment_id)
        print(is_assignment_owner)
        if self.request.user.is_admin or self.request.user.is_staff:
            return Submission.objects.filter(assignment=assignment_id)
        elif is_assignment_owner:
            return Submission.objects.filter(assignment=assignment_id, user=self.request.user)
        else:
            raise PermissionDenied({"error": "you are not signed to this assignment course"})


class SubmissionListCreateView(generics.ListCreateAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [IsAdminOrExaminerOrSubmissionOwner]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        if self.request.user.is_admin or self.request.user.is_staff:
            return Submission.objects.all()
        else:
            return Submission.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_admin or user.is_staff:
            # Allow admins and examiners to specify the user field.
            serializer.save()
        else:
            # For other users, automatically fill the user field with their own ID.
            assignment = serializer.validated_data['assignment']
            if assignment.sub_end_date and assignment.sub_end_date < timezone.now():
                print("expired assignment")

                raise ValidationError({'error': 'Assignment has already expired.'})

            serializer.save(user=user)


class SubmissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [IsAdminOrExaminerOrSubmissionOwner]
    authentication_classes = [JWTAuthentication]

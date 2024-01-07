from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef, BooleanField, Case, When, Value
from django.utils import timezone
from django.views.static import serve
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError, PermissionDenied, AuthenticationFailed, NotFound
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Course, Classroom, Assignment, Submission, CustomUser
from .permissions import IsAdminOrCourseOwner, IsAdminOrUserOwner, IsAdminOrClassroomOwner, \
    IsAdminOrExaminerOrAssignmentOwner, IsAdminOrExaminerOrSubmissionOwner, IsActivatedAccount
from .serializers import CourseSerializer, ClassroomSerializer, AssignmentSerializer, SubmissionSerializer, \
    CustomUserSerializer
from .serializers import MyTokenObtainPairSerializer
from .utils import send_activation_mail


class UserListCreateView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdminOrUserOwner, IsActivatedAccount]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        if self.request.user.is_admin:
            return CustomUser.objects.all()
        else:
            return CustomUser.objects.filter(id=self.request.user.id)

    def perform_create(self, serializer):
        # Generate a random password
        import random
        import string
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

        # Save the user instance using the serializer
        user = serializer.save(password=password)

        # Send activation mail
        send_activation_mail(user.email, password)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdminOrUserOwner, IsActivatedAccount]
    authentication_classes = [JWTAuthentication]


class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrCourseOwner, IsActivatedAccount]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        if self.request.user.is_admin:
            return Course.objects.all()
        else:
            return Course.objects.filter(classrooms__users=self.request.user)


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrCourseOwner, IsActivatedAccount]
    authentication_classes = [JWTAuthentication]


class CourseAssignmentsListView(generics.ListAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [IsAdminOrCourseOwner, IsActivatedAccount]
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
    permission_classes = [IsAdminOrClassroomOwner, IsActivatedAccount]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        if self.request.user.is_admin:
            return Classroom.objects.all()
        else:
            return Classroom.objects.filter(users=self.request.user)


class ClassroomDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    permission_classes = [IsAdminOrClassroomOwner, IsActivatedAccount]
    authentication_classes = [JWTAuthentication]


class AssignmentListCreateView(generics.ListCreateAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAdminOrExaminerOrAssignmentOwner, IsActivatedAccount]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        if self.request.user.is_admin or self.request.user.is_staff:
            return Assignment.objects.all()
        else:
            assignments = Assignment.objects.annotate(
                is_submitted=Case(
                    When(
                        Exists(
                            Submission.objects.filter(assignment=OuterRef('pk'), user=self.request.user)
                        ),
                        then=Value(True)
                    ),
                    default=Value(False),
                    output_field=BooleanField()
                )
            ).filter(course__classrooms__users=self.request.user)
            return assignments


class AssignmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAdminOrExaminerOrAssignmentOwner, IsActivatedAccount]
    authentication_classes = [JWTAuthentication]


class AssignmentSubmissionsListView(generics.ListAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [IsAdminOrExaminerOrSubmissionOwner, IsActivatedAccount]
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
    permission_classes = [IsAdminOrExaminerOrSubmissionOwner, IsActivatedAccount]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        if self.request.user.is_admin or self.request.user.is_staff:
            return Submission.objects.all()
        else:
            return Submission.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        assignment = serializer.validated_data.get('assignment')
        existing_submission = Submission.objects.filter(user=user, assignment=assignment).first()
        if existing_submission:
            raise ValidationError("You have already submitted this assignment.")
        if user.is_admin or user.is_staff:
            # Allow admins and examiners to specify the user field (even if the assignment is expired.
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
    permission_classes = [IsAdminOrExaminerOrSubmissionOwner, IsActivatedAccount]
    authentication_classes = [JWTAuthentication]


User = get_user_model()


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='User email'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Current password'),
            'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='New password'),
            'confirm_new_password': openapi.Schema(type=openapi.TYPE_STRING, description='Confirm new password'),
        },
        required=['email', 'password', 'new_password', 'confirm_new_password']
    ),
    responses={
        200: 'Token obtained successfully',
        400: 'Bad request or validation error',
        401: 'Authentication failed',
    }
)
@api_view(['POST'])
def activate(request):
    # Get data from request body
    email = request.data.get('email')
    password = request.data.get('password')
    new_password = request.data.get('new_password')
    confirm_new_password = request.data.get('confirm_new_password')

    user: CustomUser = User.objects.get(email=email)

    if not user.check_password(password):
        raise AuthenticationFailed('Bad credentials')  # Respond with a bad credentials error

    if new_password != confirm_new_password:
        return Response({'error': 'New password and confirmation do not match'}, status=status.HTTP_400_BAD_REQUEST)

    # Change the user's password and set is_active to True
    user.set_password(new_password)
    user.activated_account = True
    user.save()

    # Create a new JWT token for the user
    token_serializer = MyTokenObtainPairSerializer()
    token = token_serializer.get_token(user)

    return Response({'refresh': str(token), 'access': str(token.access_token)}, status=status.HTTP_200_OK)


def protected_serve(request, path, document_root=None, show_indexes=False):
    if not request.user.is_authenticated or not (request.user.is_admin or request.user.is_staff):
        raise NotFound("Not found")

    return serve(request, path, document_root, show_indexes)

from django.core.exceptions import BadRequest
from django.db.models import Avg, Max, Min
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from assignments.models import Assignment, CustomUser, Submission, Classroom, Course
from .serializers import StudentAnalyticsSerializer, AssignmentAnalyticsSerializer, ClassroomAnalyticsSerializer


class AssignmentAnalyticsView(APIView):
    def get(self, request, assignment_id):
        try:
            assignment = Assignment.objects.get(pk=assignment_id)
        except Assignment.DoesNotExist:
            return Response({'error': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)

        submissions = Submission.objects.filter(assignment=assignment)

        average_score = submissions.aggregate(Avg('score'))['score__avg']
        max_score = submissions.aggregate(Max('score'))['score__max']
        min_score = submissions.aggregate(Min('score'))['score__min']

        submission_count = submissions.count()

        analytics_data = {
            'submission_count': submission_count,
            'average_score': average_score,
            'max_score': max_score,
            'min_score': min_score,
        }

        serializer = AssignmentAnalyticsSerializer(analytics_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentAnalyticsView(APIView):
    def get(self, request, student_id):
        try:
            student = CustomUser.objects.get(pk=student_id)
            if student.is_admin or student.is_staff:
                raise BadRequest("User is not a student")

        except CustomUser.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        submissions = Submission.objects.filter(user=student)

        average_score = submissions.aggregate(Avg('score'))['score__avg']
        max_score = submissions.aggregate(Max('score'))['score__max']
        min_score = submissions.aggregate(Min('score'))['score__min']

        # Count the total number of submissions by the student
        submission_count = submissions.count()

        analytics_data = {
            'average_score': average_score,
            'max_score': max_score,
            'min_score': min_score,
            'submission_count': submission_count,
        }

        serializer = StudentAnalyticsSerializer(analytics_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClassroomAnalyticsView(APIView):
    def get(self, request, classroom_id):
        try:
            classroom = Classroom.objects.get(pk=classroom_id)

            courses = Course.objects.filter(classrooms=classroom)

            course_analytics_list = []

            for course in courses:
                # Filter submissions for this course within the classroom
                submissions = Submission.objects.filter(assignment__course=course,
                                                        assignment__course__classrooms=classroom)

                # Calculate metrics for this course
                submissions_count = submissions.count()
                avg_score = submissions.aggregate(Avg('score'))['score__avg']
                max_score = submissions.aggregate(Max('score'))['score__max']
                min_score = submissions.aggregate(Min('score'))['score__min']

                # Add course analytics data to the list
                course_analytics = {
                    'course_name': course.name,
                    'submissions_count': submissions_count,
                    'avg_score': avg_score,
                    'max_score': max_score,
                    'min_score': min_score,
                }
                course_analytics_list.append(course_analytics)

            # Calculate overall metrics for the classroom
            classroom_submissions = Submission.objects.filter(assignment__course__classrooms=classroom)
            submissions_count = classroom_submissions.count()
            avg_score = classroom_submissions.aggregate(Avg('score'))['score__avg']
            max_score = classroom_submissions.aggregate(Max('score'))['score__max']
            min_score = classroom_submissions.aggregate(Min('score'))['score__min']

            # Get top five students with the highest average scores in the classroom
            top_students = classroom_submissions.values('user__id', 'user__first_name', 'user__last_name').annotate(
                avg_score=Avg('score')).order_by('-avg_score')[:5]

            # Get lowest five students with the lowest average scores in the classroom
            lowest_students = classroom_submissions.values('user__id', 'user__first_name', 'user__last_name').annotate(
                avg_score=Avg('score')).order_by('avg_score')[:5]

            classroom_analytics = {
                'classroom_name': classroom.name,
                'submissions_count': submissions_count,
                'avg_score': avg_score,
                'max_score': max_score,
                'min_score': min_score,
                'top_students': top_students,
                'lowest_students': lowest_students,
                'related_courses': course_analytics_list,
            }

            serializer = ClassroomAnalyticsSerializer(classroom_analytics)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Classroom.DoesNotExist:
            return Response({'error': 'Classroom not found'}, status=status.HTTP_404_NOT_FOUND)

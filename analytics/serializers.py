from rest_framework import serializers


class AssignmentAnalyticsSerializer(serializers.Serializer):
    submission_count = serializers.IntegerField()
    average_score = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    max_score = serializers.IntegerField(read_only=True)
    min_score = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ('submission_count', 'average_score', 'max_score', 'min_score',)


class StudentAnalyticsSerializer(serializers.Serializer):
    submission_count = serializers.IntegerField()
    average_score = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    max_score = serializers.IntegerField(read_only=True)
    min_score = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ('submission_count', 'average_score', 'max_score', 'min_score',)


class ClassroomAnalyticsSerializer(serializers.Serializer):
    classroom_name = serializers.CharField()
    submissions_count = serializers.IntegerField()
    avg_score = serializers.DecimalField(max_digits=5, decimal_places=2)
    max_score = serializers.IntegerField()
    min_score = serializers.IntegerField()
    top_students = serializers.ListField(child=serializers.DictField(), required=False)
    lowest_students = serializers.ListField(child=serializers.DictField(), required=False)
    related_courses = serializers.ListField(child=serializers.DictField(), required=False)

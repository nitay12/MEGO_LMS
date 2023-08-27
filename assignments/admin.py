from django.contrib import admin

from .models import CustomUser, Classroom, Course, Assignment, Submission


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(is_staff=True)


admin.site.register(Classroom)
admin.site.register(Course)
admin.site.register(Assignment)
admin.site.register(Submission)

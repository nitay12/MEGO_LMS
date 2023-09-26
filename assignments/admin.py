from django.contrib import admin

from .models import CustomUser, Classroom, Course, Assignment, Submission


# Customizing the admin interface for CustomUser model
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'activated_account', 'is_staff')
    list_filter = ('activated_account', 'is_staff', 'classrooms')
    search_fields = ('email', 'first_name', 'last_name')


admin.site.register(CustomUser, CustomUserAdmin)


# Customizing the admin interface for Classroom model
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


admin.site.register(Classroom, ClassroomAdmin)


# Customizing the admin interface for Course model
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


admin.site.register(Course, CourseAdmin)


# Customizing the admin interface for Assignment model
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'sub_end_date')
    list_filter = ('course',)
    search_fields = ('title', 'course__name')


admin.site.register(Assignment, AssignmentAdmin)


# Customizing the admin interface for Submission model
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'assignment', 'sub_date', 'score')
    list_filter = ('assignment__course', 'assignment')
    search_fields = ('user__email', 'assignment__title')


admin.site.register(Submission, SubmissionAdmin)

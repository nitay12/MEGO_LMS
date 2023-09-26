from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.db import models
from django.utils import timezone
from .validators import validate_file_size


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('activated_account', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, null=False, blank=False)
    first_name = models.CharField(max_length=30, null=False, blank=False)
    last_name = models.CharField(max_length=30, null=False, blank=False)
    is_active = models.BooleanField(default=True)
    activated_account = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    username = models.CharField(max_length=30, unique=False, null=True, blank=True)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.first_name + " " + self.last_name


class Classroom(models.Model):
    name = models.CharField(max_length=100, null=False, unique=True)
    users = models.ManyToManyField('CustomUser', related_name='classrooms')

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    classrooms = models.ManyToManyField(Classroom, related_name='courses')

    def __str__(self):
        return self.name


class Assignment(models.Model):
    title = models.CharField(max_length=200, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    sub_end_date = models.DateTimeField()

    def __str__(self):
        return self.title


def generate_file_name(instance, original_filename):
    # Get assignment title, user's first name, and user's last name
    assignment_title = instance.assignment.title
    user_first_name = instance.user.first_name
    user_last_name = instance.user.last_name
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    extension = original_filename.split('.')[-1]
    # Construct the final file name
    file_name = f"submissions/{assignment_title}_{user_first_name}_{user_last_name}_{timestamp}.{extension}"

    return file_name


class Submission(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, null=False)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, null=False)
    sub_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to=generate_file_name, validators=[validate_file_size])
    comment = models.TextField(max_length=500, null=True)
    score = models.SmallIntegerField(null=False, blank=False, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'assignment')

    def __str__(self):
        return f"{self.user} - {self.assignment}"

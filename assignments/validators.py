from django.core.exceptions import ValidationError


def validate_file_size(value):
    # Maximum file size in bytes (e.g., 10 MB)
    max_size = 10 * 1024 * 1024  # 10 MB

    if value.size > max_size:
        raise ValidationError("File size exceeds the maximum allowed size (10 MB).")

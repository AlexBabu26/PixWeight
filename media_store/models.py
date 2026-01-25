import uuid
from django.conf import settings
from django.db import models

class UploadedImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="uploaded_images")
    image = models.ImageField(upload_to="uploads/%Y/%m/%d/")
    original_filename = models.CharField(max_length=255, blank=True)
    size_bytes = models.PositiveIntegerField(default=0)
    mime_type = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.original_filename or str(self.id)


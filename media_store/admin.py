from django.contrib import admin
from .models import UploadedImage

@admin.register(UploadedImage)
class UploadedImageAdmin(admin.ModelAdmin):
    list_display = ("id", "uploaded_by", "original_filename", "mime_type", "size_bytes", "created_at")
    search_fields = ("original_filename", "uploaded_by__username")
    list_filter = ("mime_type", "created_at")


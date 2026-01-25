from rest_framework import serializers
from .models import UploadedImage

class UploadedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedImage
        fields = ["id", "image", "original_filename", "size_bytes", "mime_type", "created_at"]

class UploadImageSerializer(serializers.Serializer):
    image = serializers.ImageField()


import mimetypes
from io import BytesIO

from django.conf import settings
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from PIL import Image

from .models import UploadedImage
from .serializers import UploadedImageSerializer, UploadImageSerializer

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
FORMAT_TO_MIME = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "WEBP": "image/webp",
}

class ImageUploadAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    throttle_scope = "upload"

    def post(self, request):
        ser = UploadImageSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        f = ser.validated_data["image"]

        # Size check
        if getattr(f, "size", 0) and f.size > settings.MAX_UPLOAD_BYTES:
            max_mb = settings.MAX_UPLOAD_BYTES / (1024 * 1024)
            return Response({"detail": f"File too large. Max is {max_mb:.1f}MB."}, status=400)

        # Validate image content using Pillow (more reliable than imghdr)
        mime_type = ""
        try:
            # Read file content
            f.seek(0)
            image_data = f.read()
            f.seek(0)  # Reset for saving
            
            # Try to open and verify the image
            img = Image.open(BytesIO(image_data))
            img_format = img.format
            
            # Verify format is allowed
            if not img_format or img_format not in ALLOWED_FORMATS:
                # Try fallback to filename-based detection
                guessed, _ = mimetypes.guess_type(getattr(f, "name", "") or "")
                if guessed and guessed in FORMAT_TO_MIME.values():
                    mime_type = guessed
                else:
                    return Response({
                        "detail": f"Unsupported image format: {img_format or 'unknown'}. Allowed: JPEG, PNG, WebP."
                    }, status=400)
            else:
                # Verify it's actually a valid image by attempting to load it
                img.verify()
                
                # Get mime type
                mime_type = FORMAT_TO_MIME.get(img_format) or mimetypes.guess_type(getattr(f, "name", "") or "")[0] or ""
            
        except Image.UnidentifiedImageError:
            # Fallback to mimetypes if Pillow can't identify it
            guessed, _ = mimetypes.guess_type(getattr(f, "name", "") or "")
            if guessed not in FORMAT_TO_MIME.values():
                return Response({
                    "detail": "Invalid image file or unsupported format. Allowed: JPEG, PNG, WebP."
                }, status=400)
            mime_type = guessed
        except Exception as e:
            return Response({
                "detail": f"Error validating image: {str(e)}"
            }, status=400)

        obj = UploadedImage.objects.create(
            uploaded_by=request.user,
            image=f,
            original_filename=getattr(f, "name", "") or "",
            size_bytes=getattr(f, "size", 0) or 0,
            mime_type=mime_type,
        )
        return Response(UploadedImageSerializer(obj).data, status=201)


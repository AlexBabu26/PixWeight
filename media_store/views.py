import imghdr
import mimetypes

from django.conf import settings
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UploadedImage
from .serializers import UploadedImageSerializer, UploadImageSerializer

ALLOWED_IMGHDR = {"jpeg", "png", "webp"}
IMGHDR_TO_MIME = {
    "jpeg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
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
            return Response({"detail": f"File too large. Max is {settings.MAX_UPLOAD_BYTES} bytes."}, status=400)

        # Validate image content (best-effort)
        head = f.read(512)
        f.seek(0)
        kind = imghdr.what(None, head)
        if kind not in ALLOWED_IMGHDR:
            # fallback to mimetypes (less reliable)
            guessed, _ = mimetypes.guess_type(getattr(f, "name", "") or "")
            if guessed not in IMGHDR_TO_MIME.values():
                return Response({"detail": "Unsupported image type. Allowed: jpeg, png, webp."}, status=400)

        mime_type = IMGHDR_TO_MIME.get(kind) or mimetypes.guess_type(getattr(f, "name", "") or "")[0] or ""

        obj = UploadedImage.objects.create(
            uploaded_by=request.user,
            image=f,
            original_filename=getattr(f, "name", "") or "",
            size_bytes=getattr(f, "size", 0) or 0,
            mime_type=mime_type,
        )
        return Response(UploadedImageSerializer(obj).data, status=201)


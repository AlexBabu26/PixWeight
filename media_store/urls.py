from django.urls import path
from .views import ImageUploadAPIView

urlpatterns = [
    path("upload/", ImageUploadAPIView.as_view(), name="image-upload"),
]


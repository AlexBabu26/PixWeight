from django.urls import path
from .views import (
    CreateSessionFromImageAPIView,
    SessionListAPIView,
    SessionDetailAPIView,
    SubmitAnswersAPIView,
)

urlpatterns = [
    path("", SessionListAPIView.as_view(), name="session-list"),
    path("from-image/", CreateSessionFromImageAPIView.as_view(), name="session-from-image"),
    path("<uuid:session_id>/", SessionDetailAPIView.as_view(), name="session-detail"),
    path("<uuid:session_id>/answers/", SubmitAnswersAPIView.as_view(), name="session-submit-answers"),
]


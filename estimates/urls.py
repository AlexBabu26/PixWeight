from django.urls import path
from .views import EstimateDetailAPIView, SubmitFeedbackAPIView, GetFeedbackAPIView

urlpatterns = [
    path("<uuid:estimate_id>/", EstimateDetailAPIView.as_view(), name="estimate-detail"),
    path("<uuid:estimate_id>/feedback/", SubmitFeedbackAPIView.as_view(), name="submit-feedback"),
    path("<uuid:estimate_id>/feedback/get/", GetFeedbackAPIView.as_view(), name="get-feedback"),
]


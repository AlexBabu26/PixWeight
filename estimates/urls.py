from django.urls import path
from .views import EstimateDetailAPIView

urlpatterns = [
    path("<uuid:estimate_id>/", EstimateDetailAPIView.as_view(), name="estimate-detail"),
]


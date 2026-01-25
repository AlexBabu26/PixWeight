from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterAPIView, ProfileAPIView, ForgotPasswordAPIView, ResetPasswordAPIView

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="jwt-login"),
    path("refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("profile/", ProfileAPIView.as_view(), name="profile"),
    path("forgot-password/", ForgotPasswordAPIView.as_view(), name="forgot-password"),
    path("reset-password/", ResetPasswordAPIView.as_view(), name="reset-password"),
]


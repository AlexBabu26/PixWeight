from django.urls import path
from .views import (
    LandingView, DashboardView, LoginView, RegisterView,
    QuestionsView, ResultView, HistoryView, ProfileView, HowItWorksView
)

urlpatterns = [
    path("", LandingView.as_view(), name="landing"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("history/", HistoryView.as_view(), name="history"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("how-it-works/", HowItWorksView.as_view(), name="how_it_works"),

    path("session/<uuid:session_id>/questions/", QuestionsView.as_view(), name="questions"),
    path("session/<uuid:session_id>/result/", ResultView.as_view(), name="result"),
]


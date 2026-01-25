from django.views.generic import TemplateView

class LandingView(TemplateView):
    template_name = "frontend/landing.html"

class DashboardView(TemplateView):
    template_name = "frontend/dashboard.html"

class LoginView(TemplateView):
    template_name = "frontend/login.html"

class RegisterView(TemplateView):
    template_name = "frontend/register.html"

class QuestionsView(TemplateView):
    template_name = "frontend/questions.html"

class ResultView(TemplateView):
    template_name = "frontend/result.html"

class HistoryView(TemplateView):
    template_name = "frontend/history.html"

class ProfileView(TemplateView):
    template_name = "frontend/profile.html"

class HowItWorksView(TemplateView):
    template_name = "frontend/how_it_works.html"


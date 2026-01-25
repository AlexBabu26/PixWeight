from django.contrib import admin
from .models import EstimationSession, Question, Answer

@admin.register(EstimationSession)
class EstimationSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "object_label", "created_at")
    search_fields = ("user__username", "object_label")
    list_filter = ("status", "created_at")

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "order", "answer_type", "required")
    search_fields = ("text",)

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "question", "created_at")


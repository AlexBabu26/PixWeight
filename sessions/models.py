import uuid
from django.conf import settings
from django.db import models
from media_store.models import UploadedImage

class SessionStatus(models.TextChoices):
    QUESTIONS_ASKED = "QUESTIONS_ASKED", "Questions Asked"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    ESTIMATED = "ESTIMATED", "Estimated"
    FAILED = "FAILED", "Failed"

class EstimationSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="estimation_sessions")
    image = models.ForeignKey(UploadedImage, on_delete=models.PROTECT, related_name="sessions")

    object_label = models.CharField(max_length=200, blank=True)
    object_summary = models.TextField(blank=True)
    object_json = models.JSONField(default=dict, blank=True)

    status = models.CharField(max_length=32, choices=SessionStatus.choices, default=SessionStatus.QUESTIONS_ASKED)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Question(models.Model):
    ANSWER_TYPES = (
        ("text", "Text"),
        ("number", "Number"),
        ("boolean", "Boolean"),
        ("select", "Select"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(EstimationSession, on_delete=models.CASCADE, related_name="questions")
    order = models.PositiveIntegerField(default=0)

    text = models.TextField()
    answer_type = models.CharField(max_length=16, choices=ANSWER_TYPES, default="text")
    unit = models.CharField(max_length=32, blank=True)
    options = models.JSONField(default=list, blank=True)
    required = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

class Answer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(EstimationSession, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")

    value_text = models.TextField(blank=True)
    value_number = models.FloatField(null=True, blank=True)
    value_boolean = models.BooleanField(null=True, blank=True)
    value_json = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("session", "question")]


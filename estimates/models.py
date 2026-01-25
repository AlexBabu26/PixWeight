import uuid
from django.db import models
from sessions.models import EstimationSession

class WeightEstimate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.OneToOneField(EstimationSession, on_delete=models.CASCADE, related_name="estimate")

    value_grams = models.FloatField()
    min_grams = models.FloatField()
    max_grams = models.FloatField()
    confidence = models.FloatField(default=0.3)

    unit_display = models.CharField(max_length=16, default="g")
    rationale = models.TextField(blank=True)
    raw_json = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


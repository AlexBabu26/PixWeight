from rest_framework import serializers
from .models import WeightEstimate

class WeightEstimateSerializer(serializers.ModelSerializer):
    session_id = serializers.UUIDField(source="session.id", read_only=True)

    class Meta:
        model = WeightEstimate
        fields = [
            "id",
            "session_id",
            "value_grams", "min_grams", "max_grams",
            "confidence",
            "unit_display",
            "rationale",
            "created_at",
        ]


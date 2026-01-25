from rest_framework import serializers
from .models import WeightEstimate
from .category_serializers import (
    FoodEstimateSerializer, PackageEstimateSerializer,
    PetEstimateSerializer, BodyCompositionSerializer
)


class WeightEstimateSerializer(serializers.ModelSerializer):
    session_id = serializers.UUIDField(source="session.id", read_only=True)
    
    # Category-specific details (conditional)
    food_details = FoodEstimateSerializer(read_only=True, required=False)
    package_details = PackageEstimateSerializer(read_only=True, required=False)
    pet_details = PetEstimateSerializer(read_only=True, required=False)
    body_details = BodyCompositionSerializer(read_only=True, required=False)

    class Meta:
        model = WeightEstimate
        fields = [
            "id",
            "session_id",
            "value_grams", "min_grams", "max_grams",
            "confidence",
            "unit_display",
            "rationale",
            "category",
            "category_metadata",
            # Category-specific details
            "food_details",
            "package_details",
            "pet_details",
            "body_details",
            "created_at",
        ]


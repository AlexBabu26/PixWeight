"""
Serializers for category-specific weight estimate details.
"""

from rest_framework import serializers
from .models import (
    FoodEstimate, PackageEstimate, PetEstimate, 
    BodyCompositionEstimate, WeightFeedback
)


class FoodEstimateSerializer(serializers.ModelSerializer):
    """Serializer for food nutrition details"""
    food_reference_name = serializers.CharField(source="food_reference.name", read_only=True, default=None)
    
    class Meta:
        model = FoodEstimate
        fields = [
            "id",
            "food_reference", "food_reference_name",
            "estimated_calories", "estimated_protein", 
            "estimated_carbs", "estimated_fat", "estimated_fiber",
            "is_cooked", "portion_status",
            "created_at",
        ]


class PackageEstimateSerializer(serializers.ModelSerializer):
    """Serializer for package shipping details"""
    
    class Meta:
        model = PackageEstimate
        fields = [
            "id",
            "length_cm", "width_cm", "height_cm",
            "volumetric_weight_g", "chargeable_weight_g",
            "estimated_shipping_costs",
            "is_fragile", "destination_type",
            "created_at",
        ]


class PetEstimateSerializer(serializers.ModelSerializer):
    """Serializer for pet health assessment"""
    breed_reference_name = serializers.CharField(source="breed_reference.breed", read_only=True, default=None)
    
    class Meta:
        model = PetEstimate
        fields = [
            "id",
            "species", "breed", "breed_reference", "breed_reference_name",
            "age_category", "gender", "is_neutered",
            "health_status", 
            "ideal_weight_min", "ideal_weight_max",
            "weight_recommendation",
            "created_at",
        ]


class BodyCompositionSerializer(serializers.ModelSerializer):
    """Serializer for person body composition analysis"""
    bmi_category_name = serializers.CharField(source="bmi_category_ref.name", read_only=True, default=None)
    
    class Meta:
        model = BodyCompositionEstimate
        fields = [
            "id",
            "height_cm", "age", "gender", "activity_level",
            "bmi", "bmi_category", "bmi_category_ref", "bmi_category_name",
            "ideal_weight_min_kg", "ideal_weight_max_kg",
            "body_fat_estimate", "lean_mass_estimate",
            "health_recommendation",
            "created_at",
        ]


class WeightFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for weight estimate feedback"""
    
    class Meta:
        model = WeightFeedback
        fields = [
            "id",
            "actual_weight_grams",
            "accuracy_rating",
            "user_notes",
            "helpful",
            "error_grams",
            "error_percentage",
            "created_at",
        ]
        read_only_fields = ["error_grams", "error_percentage", "created_at"]

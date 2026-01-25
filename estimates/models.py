import uuid
from django.db import models
from sessions.models import EstimationSession


class CategoryChoices(models.TextChoices):
    """Categories for weight estimation"""
    FOOD = "food", "Food"
    PACKAGE = "package", "Package"
    PET = "pet", "Pet"
    PERSON = "person", "Person"
    GENERAL = "general", "General"


class WeightEstimate(models.Model):
    """Base weight estimate model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.OneToOneField(EstimationSession, on_delete=models.CASCADE, related_name="estimate")

    value_grams = models.FloatField()
    min_grams = models.FloatField()
    max_grams = models.FloatField()
    confidence = models.FloatField(default=0.3)

    unit_display = models.CharField(max_length=16, default="g")
    rationale = models.TextField(blank=True)
    raw_json = models.JSONField(default=dict, blank=True)
    
    # Category detection
    category = models.CharField(max_length=20, choices=CategoryChoices.choices, default=CategoryChoices.GENERAL)
    category_metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.category} - {self.value_grams}g"


# ============================================
# FOOD / NUTRITION MODELS
# ============================================

class FoodNutrition(models.Model):
    """Static reference database for common foods"""
    name = models.CharField(max_length=100, unique=True)
    aliases = models.JSONField(default=list, blank=True, help_text="Alternative names for fuzzy matching")
    
    # Nutrition per 100g
    calories_per_100g = models.FloatField()
    protein_per_100g = models.FloatField(default=0)
    carbs_per_100g = models.FloatField(default=0)
    fat_per_100g = models.FloatField(default=0)
    fiber_per_100g = models.FloatField(default=0)
    
    food_category = models.CharField(max_length=50, blank=True, help_text="fruit, vegetable, meat, dairy, etc.")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Food Nutrition Data"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.calories_per_100g} kcal/100g)"


class FoodEstimate(models.Model):
    """Extended estimate data for food items"""
    estimate = models.OneToOneField(WeightEstimate, on_delete=models.CASCADE, related_name="food_details")
    food_reference = models.ForeignKey(FoodNutrition, null=True, blank=True, on_delete=models.SET_NULL)
    
    # Calculated nutrition values
    estimated_calories = models.FloatField()
    estimated_protein = models.FloatField(default=0)
    estimated_carbs = models.FloatField(default=0)
    estimated_fat = models.FloatField(default=0)
    estimated_fiber = models.FloatField(default=0)
    
    # Additional food-specific data
    is_cooked = models.BooleanField(default=False)
    portion_status = models.CharField(max_length=50, blank=True)  # whole, partial, etc.
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Food: {self.estimated_calories} kcal"


# ============================================
# PACKAGE / SHIPPING MODELS
# ============================================

class ShippingCarrier(models.Model):
    """Static carrier rate database"""
    name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=50, help_text="Ground, Express, Overnight, etc.")
    
    # Pricing
    base_rate = models.DecimalField(max_digits=10, decimal_places=2)
    rate_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    max_weight_kg = models.FloatField()
    
    # Volumetric calculation
    volumetric_divisor = models.IntegerField(default=5000, help_text="Divisor for volumetric weight (L×W×H)/divisor")
    
    # Additional info
    is_international = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name", "service_type"]

    def __str__(self):
        return f"{self.name} - {self.service_type}"


class PackageEstimate(models.Model):
    """Extended estimate data for packages"""
    estimate = models.OneToOneField(WeightEstimate, on_delete=models.CASCADE, related_name="package_details")
    
    # Dimensions
    length_cm = models.FloatField(null=True, blank=True)
    width_cm = models.FloatField(null=True, blank=True)
    height_cm = models.FloatField(null=True, blank=True)
    
    # Weight calculations
    volumetric_weight_g = models.FloatField(null=True, blank=True)
    chargeable_weight_g = models.FloatField()  # max(actual, volumetric)
    
    # Shipping costs
    estimated_shipping_costs = models.JSONField(default=dict, help_text="Dictionary of carrier: cost")
    
    # Additional package info
    is_fragile = models.BooleanField(default=False)
    destination_type = models.CharField(max_length=20, blank=True)  # domestic, international
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Package: {self.chargeable_weight_g}g"


# ============================================
# PET / HEALTH MODELS
# ============================================

class BreedReference(models.Model):
    """Static breed weight standards"""
    species = models.CharField(max_length=50, help_text="dog, cat, rabbit, etc.")
    breed = models.CharField(max_length=100)
    aliases = models.JSONField(default=list, blank=True, help_text="Alternative breed names")
    
    # Weight ranges by life stage (in kg)
    puppy_min_kg = models.FloatField(null=True, blank=True)
    puppy_max_kg = models.FloatField(null=True, blank=True)
    adult_min_kg = models.FloatField()
    adult_max_kg = models.FloatField()
    senior_min_kg = models.FloatField(null=True, blank=True)
    senior_max_kg = models.FloatField(null=True, blank=True)
    
    # Health thresholds (percentage of ideal)
    underweight_threshold = models.FloatField(default=0.85, help_text="Below 85% of ideal = underweight")
    overweight_threshold = models.FloatField(default=1.15, help_text="Above 115% of ideal = overweight")
    
    # Additional info
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["species", "breed"]
        unique_together = ["species", "breed"]

    def __str__(self):
        return f"{self.breed} ({self.species}): {self.adult_min_kg}-{self.adult_max_kg}kg"


class PetEstimate(models.Model):
    """Extended estimate data for pets"""
    estimate = models.OneToOneField(WeightEstimate, on_delete=models.CASCADE, related_name="pet_details")
    
    # Pet identification
    species = models.CharField(max_length=50)
    breed = models.CharField(max_length=100, blank=True)
    breed_reference = models.ForeignKey(BreedReference, null=True, blank=True, on_delete=models.SET_NULL)
    
    # Pet characteristics
    age_category = models.CharField(max_length=20, blank=True, help_text="puppy, adult, senior")
    gender = models.CharField(max_length=10, blank=True)
    is_neutered = models.BooleanField(null=True, blank=True)
    
    # Health assessment
    health_status = models.CharField(max_length=20, blank=True, help_text="underweight, healthy, overweight")
    ideal_weight_min = models.FloatField(null=True, blank=True)
    ideal_weight_max = models.FloatField(null=True, blank=True)
    weight_recommendation = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pet: {self.species} - {self.health_status}"


# ============================================
# PERSON / BODY COMPOSITION MODELS
# ============================================

class BMICategory(models.Model):
    """Static BMI reference data"""
    name = models.CharField(max_length=20, unique=True)
    min_bmi = models.FloatField()
    max_bmi = models.FloatField()
    description = models.TextField()
    recommendation = models.TextField()
    
    # Visual indicator color
    color_code = models.CharField(max_length=20, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "BMI Categories"
        ordering = ["min_bmi"]

    def __str__(self):
        return f"{self.name} (BMI {self.min_bmi}-{self.max_bmi})"


class BodyCompositionEstimate(models.Model):
    """Extended estimate data for people"""
    estimate = models.OneToOneField(WeightEstimate, on_delete=models.CASCADE, related_name="body_details")
    
    # Required measurements
    height_cm = models.FloatField()
    
    # Optional demographics
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    activity_level = models.CharField(max_length=50, blank=True)
    
    # Calculated values
    bmi = models.FloatField()
    bmi_category = models.CharField(max_length=20)
    bmi_category_ref = models.ForeignKey(BMICategory, null=True, blank=True, on_delete=models.SET_NULL)
    
    # Ideal weight range (BMI 18.5-24.9)
    ideal_weight_min_kg = models.FloatField()
    ideal_weight_max_kg = models.FloatField()
    
    # Body composition estimates
    body_fat_estimate = models.FloatField(null=True, blank=True, help_text="Estimated body fat percentage")
    lean_mass_estimate = models.FloatField(null=True, blank=True)
    
    # Health recommendation
    health_recommendation = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Person: BMI {self.bmi:.1f} ({self.bmi_category})"


# ============================================
# FEEDBACK SYSTEM
# ============================================

class WeightFeedback(models.Model):
    """User feedback on estimation accuracy"""
    estimate = models.OneToOneField(WeightEstimate, on_delete=models.CASCADE, related_name="feedback")
    
    # Actual weight provided by user
    actual_weight_grams = models.FloatField()
    
    # Accuracy rating (1-5 stars)
    accuracy_rating = models.IntegerField(null=True, blank=True, help_text="1-5 star rating")
    
    # User feedback
    user_notes = models.TextField(blank=True)
    helpful = models.BooleanField(default=True, help_text="Was this estimation helpful?")
    
    # Calculated accuracy
    error_grams = models.FloatField(null=True, blank=True)
    error_percentage = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        # Calculate error automatically
        if self.actual_weight_grams and self.estimate:
            self.error_grams = abs(self.actual_weight_grams - self.estimate.value_grams)
            if self.actual_weight_grams > 0:
                self.error_percentage = (self.error_grams / self.actual_weight_grams) * 100
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Feedback: {self.accuracy_rating}★ - {self.error_percentage:.1f}% error"


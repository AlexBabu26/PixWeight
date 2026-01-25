"""
Category-specific calculation functions for weight estimates.

This module provides post-estimation calculations for:
- Food: Nutrition information (calories, macros)
- Package: Shipping cost estimates
- Pet: Health assessment based on breed standards
- Person: BMI and body composition analysis
"""

from typing import Dict, Any, Optional, List, Tuple
from decimal import Decimal
from django.db.models import Q
from .models import FoodNutrition, ShippingCarrier, BreedReference, BMICategory


# ============================================
# FOOD / NUTRITION CALCULATIONS
# ============================================

def fuzzy_match_food(food_name: str) -> Optional[FoodNutrition]:
    """
    Fuzzy match food name to FoodNutrition database.
    
    Args:
        food_name: Name of food from object label
        
    Returns:
        FoodNutrition object if match found, None otherwise
    """
    if not food_name:
        return None
    
    food_name_lower = food_name.lower().strip()
    
    # Try exact match first
    food = FoodNutrition.objects.filter(name__iexact=food_name_lower).first()
    if food:
        return food
    
    # Try partial match on name
    food = FoodNutrition.objects.filter(name__icontains=food_name_lower).first()
    if food:
        return food
    
    # Try matching against aliases
    foods = FoodNutrition.objects.all()
    for f in foods:
        for alias in f.aliases:
            if alias.lower() in food_name_lower or food_name_lower in alias.lower():
                return f
    
    return None


def calculate_nutrition(weight_grams: float, food_name: str, answers: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Calculate calories and macros from weight and food name.
    
    Args:
        weight_grams: Estimated weight in grams
        food_name: Name of the food item
        answers: User answers (for cooking status, portion, etc.)
        
    Returns:
        Dictionary with nutrition data and reference info
    """
    # Try to find food in database
    food_ref = fuzzy_match_food(food_name)
    
    if not food_ref:
        return {
            "found": False,
            "food_name": food_name,
            "message": "Food not found in nutrition database",
            "estimated_calories": None,
            "estimated_protein": None,
            "estimated_carbs": None,
            "estimated_fat": None,
            "estimated_fiber": None,
        }
    
    # Calculate multiplier (weight / 100g)
    multiplier = weight_grams / 100.0
    
    # Calculate nutrition values
    calories = food_ref.calories_per_100g * multiplier
    protein = food_ref.protein_per_100g * multiplier
    carbs = food_ref.carbs_per_100g * multiplier
    fat = food_ref.fat_per_100g * multiplier
    fiber = food_ref.fiber_per_100g * multiplier
    
    # Adjust for cooking status if available
    cooking_adjustment = 1.0
    if answers:
        cooking_status = answers.get("is_cooked", "").lower()
        if "cooked" in cooking_status and food_ref.food_category in ["meat", "seafood", "grain"]:
            # Cooked items may have lost water weight, so calories are more concentrated
            cooking_adjustment = 1.1
    
    return {
        "found": True,
        "food_reference_id": food_ref.id,
        "food_name": food_ref.name,
        "food_category": food_ref.food_category,
        "estimated_calories": round(calories * cooking_adjustment, 1),
        "estimated_protein": round(protein * cooking_adjustment, 1),
        "estimated_carbs": round(carbs * cooking_adjustment, 1),
        "estimated_fat": round(fat * cooking_adjustment, 1),
        "estimated_fiber": round(fiber * cooking_adjustment, 1),
        "per_100g": {
            "calories": food_ref.calories_per_100g,
            "protein": food_ref.protein_per_100g,
            "carbs": food_ref.carbs_per_100g,
            "fat": food_ref.fat_per_100g,
            "fiber": food_ref.fiber_per_100g,
        }
    }


# ============================================
# PACKAGE / SHIPPING CALCULATIONS
# ============================================

def calculate_volumetric_weight(length_cm: float, width_cm: float, height_cm: float, divisor: int = 5000) -> float:
    """
    Calculate volumetric weight in grams.
    
    Formula: (L × W × H) / divisor
    
    Args:
        length_cm: Length in centimeters
        width_cm: Width in centimeters
        height_cm: Height in centimeters
        divisor: Volumetric divisor (default 5000 for most carriers)
        
    Returns:
        Volumetric weight in grams
    """
    volume = length_cm * width_cm * height_cm
    volumetric_kg = volume / divisor
    return volumetric_kg * 1000  # Convert to grams


def calculate_shipping_costs(weight_grams: float, dimensions: Dict[str, float], 
                            destination_type: str = "Domestic") -> Dict[str, Any]:
    """
    Calculate shipping costs for all available carriers.
    
    Args:
        weight_grams: Actual weight in grams
        dimensions: Dict with length_cm, width_cm, height_cm
        destination_type: "Domestic" or "International"
        
    Returns:
        Dictionary with shipping cost data
    """
    length_cm = dimensions.get("length_cm", 0)
    width_cm = dimensions.get("width_cm", 0)
    height_cm = dimensions.get("height_cm", 0)
    
    # Calculate volumetric weight
    volumetric_weight_g = None
    if length_cm and width_cm and height_cm:
        volumetric_weight_g = calculate_volumetric_weight(length_cm, width_cm, height_cm)
    
    # Chargeable weight is max of actual and volumetric
    chargeable_weight_g = weight_grams
    if volumetric_weight_g:
        chargeable_weight_g = max(weight_grams, volumetric_weight_g)
    
    chargeable_weight_kg = chargeable_weight_g / 1000.0
    
    # Get appropriate carriers
    is_international = destination_type.lower() == "international"
    carriers = ShippingCarrier.objects.filter(is_active=True)
    if is_international:
        carriers = carriers.filter(is_international=True)
    else:
        carriers = carriers.filter(is_international=False)
    
    # Calculate costs for each carrier
    shipping_costs = {}
    carrier_details = []
    
    for carrier in carriers:
        # Check if package exceeds max weight
        if chargeable_weight_kg > carrier.max_weight_kg:
            continue
        
        # Calculate cost: base_rate + (weight_kg * rate_per_kg)
        cost = float(carrier.base_rate) + (chargeable_weight_kg * float(carrier.rate_per_kg))
        cost = round(cost, 2)
        
        key = f"{carrier.name} - {carrier.service_type}"
        shipping_costs[key] = cost
        
        carrier_details.append({
            "carrier": carrier.name,
            "service": carrier.service_type,
            "cost": cost,
            "max_weight_kg": carrier.max_weight_kg,
        })
    
    # Sort by cost
    carrier_details.sort(key=lambda x: x["cost"])
    
    return {
        "dimensions": {
            "length_cm": length_cm,
            "width_cm": width_cm,
            "height_cm": height_cm,
        },
        "actual_weight_g": weight_grams,
        "volumetric_weight_g": volumetric_weight_g,
        "chargeable_weight_g": chargeable_weight_g,
        "destination_type": destination_type,
        "shipping_costs": shipping_costs,
        "carrier_details": carrier_details,
        "cheapest_option": carrier_details[0] if carrier_details else None,
    }


# ============================================
# PET / HEALTH ASSESSMENT
# ============================================

def fuzzy_match_breed(species: str, breed_name: str) -> Optional[BreedReference]:
    """
    Fuzzy match breed name to BreedReference database.
    
    Args:
        species: Pet species (dog, cat, etc.)
        breed_name: Breed name
        
    Returns:
        BreedReference object if match found, None otherwise
    """
    if not breed_name or not species:
        return None
    
    species_lower = species.lower().strip()
    breed_lower = breed_name.lower().strip()
    
    # Try exact match
    breed = BreedReference.objects.filter(
        species__iexact=species_lower,
        breed__iexact=breed_lower
    ).first()
    if breed:
        return breed
    
    # Try partial match
    breed = BreedReference.objects.filter(
        species__iexact=species_lower,
        breed__icontains=breed_lower
    ).first()
    if breed:
        return breed
    
    # Try matching against aliases
    breeds = BreedReference.objects.filter(species__iexact=species_lower)
    for b in breeds:
        for alias in b.aliases:
            if alias.lower() in breed_lower or breed_lower in alias.lower():
                return b
    
    return None


def assess_pet_health(weight_kg: float, species: str, breed_name: str = "", 
                     age_category: str = "adult") -> Dict[str, Any]:
    """
    Assess pet health vs breed standards.
    
    Args:
        weight_kg: Pet weight in kilograms
        species: Pet species (dog, cat, etc.)
        breed_name: Breed name (optional)
        age_category: "puppy", "adult", or "senior"
        
    Returns:
        Dictionary with health assessment
    """
    # Try to find breed in database
    breed_ref = None
    if breed_name:
        breed_ref = fuzzy_match_breed(species, breed_name)
    
    if not breed_ref:
        return {
            "found": False,
            "species": species,
            "breed_name": breed_name or "Unknown",
            "weight_kg": weight_kg,
            "health_status": "unknown",
            "message": f"Breed '{breed_name}' not found in database for {species}",
            "ideal_weight_min": None,
            "ideal_weight_max": None,
            "weight_recommendation": "Unable to assess without breed information.",
        }
    
    # Get appropriate weight range for age category
    age_cat_lower = age_category.lower()
    if "puppy" in age_cat_lower or "kitten" in age_cat_lower:
        ideal_min = breed_ref.puppy_min_kg or breed_ref.adult_min_kg * 0.5
        ideal_max = breed_ref.puppy_max_kg or breed_ref.adult_max_kg * 0.6
    elif "senior" in age_cat_lower:
        ideal_min = breed_ref.senior_min_kg or breed_ref.adult_min_kg
        ideal_max = breed_ref.senior_max_kg or breed_ref.adult_max_kg
    else:  # adult
        ideal_min = breed_ref.adult_min_kg
        ideal_max = breed_ref.adult_max_kg
    
    # Calculate midpoint of ideal range
    ideal_mid = (ideal_min + ideal_max) / 2
    
    # Assess health status
    underweight_threshold = ideal_mid * breed_ref.underweight_threshold
    overweight_threshold = ideal_mid * breed_ref.overweight_threshold
    
    if weight_kg < underweight_threshold:
        health_status = "underweight"
        recommendation = f"This {breed_ref.breed} appears underweight. Consider consulting a veterinarian about healthy weight gain. Ensure proper nutrition and rule out health issues."
    elif weight_kg > overweight_threshold:
        health_status = "overweight"
        recommendation = f"This {breed_ref.breed} appears overweight. Consider a balanced diet and increased exercise. Consult your veterinarian for a weight management plan."
    elif weight_kg < ideal_min:
        health_status = "slightly_underweight"
        recommendation = f"This {breed_ref.breed} is slightly below ideal weight. Monitor closely and ensure adequate nutrition."
    elif weight_kg > ideal_max:
        health_status = "slightly_overweight"
        recommendation = f"This {breed_ref.breed} is slightly above ideal weight. Consider portion control and regular exercise."
    else:
        health_status = "healthy"
        recommendation = f"This {breed_ref.breed} appears to be at a healthy weight! Maintain current diet and exercise routine."
    
    # Calculate percentage of ideal
    percent_of_ideal = (weight_kg / ideal_mid) * 100
    
    return {
        "found": True,
        "breed_reference_id": breed_ref.id,
        "species": breed_ref.species,
        "breed_name": breed_ref.breed,
        "weight_kg": weight_kg,
        "age_category": age_category,
        "health_status": health_status,
        "ideal_weight_min": round(ideal_min, 1),
        "ideal_weight_max": round(ideal_max, 1),
        "ideal_weight_mid": round(ideal_mid, 1),
        "percent_of_ideal": round(percent_of_ideal, 1),
        "weight_recommendation": recommendation,
        "breed_description": breed_ref.description,
    }


# ============================================
# PERSON / BMI CALCULATIONS
# ============================================

def calculate_bmi_insights(weight_kg: float, height_cm: float, age: Optional[int] = None, 
                          gender: Optional[str] = None, activity_level: Optional[str] = None) -> Dict[str, Any]:
    """
    Calculate BMI and body composition estimates.
    
    Args:
        weight_kg: Weight in kilograms
        height_cm: Height in centimeters
        age: Age in years (optional, for body fat estimation)
        gender: Gender (optional, for body fat estimation)
        activity_level: Activity level (optional)
        
    Returns:
        Dictionary with BMI analysis and recommendations
    """
    # Calculate BMI
    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m ** 2)
    
    # Find BMI category
    bmi_category = BMICategory.objects.filter(
        min_bmi__lte=bmi,
        max_bmi__gte=bmi
    ).first()
    
    if not bmi_category:
        # Default categorization
        if bmi < 18.5:
            category_name = "Underweight"
            recommendation = "Consider consulting a healthcare provider about healthy weight gain."
        elif bmi < 25:
            category_name = "Normal"
            recommendation = "You're in a healthy weight range. Maintain your current lifestyle!"
        elif bmi < 30:
            category_name = "Overweight"
            recommendation = "Consider moderate lifestyle changes for optimal health."
        else:
            category_name = "Obese"
            recommendation = "Consulting a healthcare provider is recommended."
        color_code = "#6b7280"
    else:
        category_name = bmi_category.name
        recommendation = bmi_category.recommendation
        color_code = bmi_category.color_code
    
    # Calculate ideal weight range (BMI 18.5-24.9)
    ideal_min_kg = 18.5 * (height_m ** 2)
    ideal_max_kg = 24.9 * (height_m ** 2)
    
    # Estimate body fat percentage (if age and gender provided)
    # Formula: Body Fat % = (1.20 × BMI) + (0.23 × Age) − (10.8 × gender) − 5.4
    # where gender = 1 for male, 0 for female
    body_fat_estimate = None
    lean_mass_estimate = None
    
    if age and gender:
        gender_factor = 1 if gender.lower() in ["male", "m"] else 0
        body_fat_pct = (1.20 * bmi) + (0.23 * age) - (10.8 * gender_factor) - 5.4
        body_fat_pct = max(5, min(50, body_fat_pct))  # Clamp to reasonable range
        body_fat_estimate = round(body_fat_pct, 1)
        
        # Calculate lean mass
        fat_mass_kg = (body_fat_pct / 100) * weight_kg
        lean_mass_estimate = round(weight_kg - fat_mass_kg, 1)
    
    # Build response
    return {
        "weight_kg": weight_kg,
        "height_cm": height_cm,
        "height_m": round(height_m, 2),
        "bmi": round(bmi, 1),
        "bmi_category": category_name,
        "bmi_category_id": bmi_category.id if bmi_category else None,
        "bmi_color_code": color_code,
        "ideal_weight_min_kg": round(ideal_min_kg, 1),
        "ideal_weight_max_kg": round(ideal_max_kg, 1),
        "body_fat_estimate": body_fat_estimate,
        "lean_mass_estimate": lean_mass_estimate,
        "age": age,
        "gender": gender,
        "activity_level": activity_level,
        "health_recommendation": recommendation,
        "disclaimer": "This is an estimate for educational purposes only. Consult a healthcare professional for medical advice.",
    }


# ============================================
# HELPER FUNCTIONS
# ============================================

def extract_answer_value(answers: List[Dict], question_text: str, default: Any = None) -> Any:
    """
    Extract answer value from answers list by question text.
    
    Args:
        answers: List of answer dictionaries
        question_text: Question text to search for (case-insensitive partial match)
        default: Default value if not found
        
    Returns:
        Answer value or default
    """
    question_lower = question_text.lower()
    for answer in answers:
        q_text = answer.get("question", "").lower()
        if question_lower in q_text or q_text in question_lower:
            return answer.get("answer", default)
    return default

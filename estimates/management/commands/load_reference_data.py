"""
Management command to load reference data for category-specific estimations.

Usage: python manage.py load_reference_data
"""

from django.core.management.base import BaseCommand
from estimates.models import FoodNutrition, ShippingCarrier, BreedReference, BMICategory


class Command(BaseCommand):
    help = 'Load reference data for food nutrition, shipping carriers, pet breeds, and BMI categories'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Loading reference data...'))
        
        # Clear existing data
        self.stdout.write('Clearing existing reference data...')
        FoodNutrition.objects.all().delete()
        ShippingCarrier.objects.all().delete()
        BreedReference.objects.all().delete()
        BMICategory.objects.all().delete()
        
        # Load all reference data
        self.load_food_nutrition()
        self.load_shipping_carriers()
        self.load_breed_references()
        self.load_bmi_categories()
        
        self.stdout.write(self.style.SUCCESS('All reference data loaded successfully!'))
    
    def load_food_nutrition(self):
        """Load nutrition data for 50+ common foods"""
        self.stdout.write('Loading food nutrition data...')
        
        foods = [
            # Fruits
            {"name": "apple", "aliases": ["red apple", "green apple", "granny smith"], 
             "calories_per_100g": 52, "protein_per_100g": 0.3, "carbs_per_100g": 14, 
             "fat_per_100g": 0.2, "fiber_per_100g": 2.4, "food_category": "fruit"},
            {"name": "banana", "aliases": ["ripe banana", "plantain"], 
             "calories_per_100g": 89, "protein_per_100g": 1.1, "carbs_per_100g": 23, 
             "fat_per_100g": 0.3, "fiber_per_100g": 2.6, "food_category": "fruit"},
            {"name": "orange", "aliases": ["navel orange", "blood orange"], 
             "calories_per_100g": 47, "protein_per_100g": 0.9, "carbs_per_100g": 12, 
             "fat_per_100g": 0.1, "fiber_per_100g": 2.4, "food_category": "fruit"},
            {"name": "grape", "aliases": ["grapes", "green grape", "red grape"], 
             "calories_per_100g": 69, "protein_per_100g": 0.7, "carbs_per_100g": 18, 
             "fat_per_100g": 0.2, "fiber_per_100g": 0.9, "food_category": "fruit"},
            {"name": "watermelon", "aliases": ["water melon"], 
             "calories_per_100g": 30, "protein_per_100g": 0.6, "carbs_per_100g": 8, 
             "fat_per_100g": 0.2, "fiber_per_100g": 0.4, "food_category": "fruit"},
            {"name": "strawberry", "aliases": ["strawberries"], 
             "calories_per_100g": 32, "protein_per_100g": 0.7, "carbs_per_100g": 8, 
             "fat_per_100g": 0.3, "fiber_per_100g": 2.0, "food_category": "fruit"},
            {"name": "mango", "aliases": ["mangoes"], 
             "calories_per_100g": 60, "protein_per_100g": 0.8, "carbs_per_100g": 15, 
             "fat_per_100g": 0.4, "fiber_per_100g": 1.6, "food_category": "fruit"},
            {"name": "pineapple", "aliases": ["pine apple"], 
             "calories_per_100g": 50, "protein_per_100g": 0.5, "carbs_per_100g": 13, 
             "fat_per_100g": 0.1, "fiber_per_100g": 1.4, "food_category": "fruit"},
            {"name": "avocado", "aliases": ["avacado"], 
             "calories_per_100g": 160, "protein_per_100g": 2.0, "carbs_per_100g": 9, 
             "fat_per_100g": 15, "fiber_per_100g": 7.0, "food_category": "fruit"},
            {"name": "peach", "aliases": ["peaches"], 
             "calories_per_100g": 39, "protein_per_100g": 0.9, "carbs_per_100g": 10, 
             "fat_per_100g": 0.3, "fiber_per_100g": 1.5, "food_category": "fruit"},
            
            # Vegetables
            {"name": "tomato", "aliases": ["tomatoes", "cherry tomato"], 
             "calories_per_100g": 18, "protein_per_100g": 0.9, "carbs_per_100g": 4, 
             "fat_per_100g": 0.2, "fiber_per_100g": 1.2, "food_category": "vegetable"},
            {"name": "carrot", "aliases": ["carrots"], 
             "calories_per_100g": 41, "protein_per_100g": 0.9, "carbs_per_100g": 10, 
             "fat_per_100g": 0.2, "fiber_per_100g": 2.8, "food_category": "vegetable"},
            {"name": "broccoli", "aliases": ["brocoli"], 
             "calories_per_100g": 34, "protein_per_100g": 2.8, "carbs_per_100g": 7, 
             "fat_per_100g": 0.4, "fiber_per_100g": 2.6, "food_category": "vegetable"},
            {"name": "lettuce", "aliases": ["iceberg lettuce", "romaine"], 
             "calories_per_100g": 15, "protein_per_100g": 1.4, "carbs_per_100g": 3, 
             "fat_per_100g": 0.2, "fiber_per_100g": 1.3, "food_category": "vegetable"},
            {"name": "cucumber", "aliases": ["cucumbers"], 
             "calories_per_100g": 16, "protein_per_100g": 0.7, "carbs_per_100g": 4, 
             "fat_per_100g": 0.1, "fiber_per_100g": 0.5, "food_category": "vegetable"},
            {"name": "potato", "aliases": ["potatoes", "russet potato"], 
             "calories_per_100g": 77, "protein_per_100g": 2.0, "carbs_per_100g": 17, 
             "fat_per_100g": 0.1, "fiber_per_100g": 2.2, "food_category": "vegetable"},
            {"name": "onion", "aliases": ["onions", "yellow onion", "red onion"], 
             "calories_per_100g": 40, "protein_per_100g": 1.1, "carbs_per_100g": 9, 
             "fat_per_100g": 0.1, "fiber_per_100g": 1.7, "food_category": "vegetable"},
            {"name": "bell pepper", "aliases": ["pepper", "red pepper", "green pepper"], 
             "calories_per_100g": 31, "protein_per_100g": 1.0, "carbs_per_100g": 6, 
             "fat_per_100g": 0.3, "fiber_per_100g": 2.1, "food_category": "vegetable"},
            {"name": "spinach", "aliases": ["baby spinach"], 
             "calories_per_100g": 23, "protein_per_100g": 2.9, "carbs_per_100g": 4, 
             "fat_per_100g": 0.4, "fiber_per_100g": 2.2, "food_category": "vegetable"},
            {"name": "cauliflower", "aliases": [], 
             "calories_per_100g": 25, "protein_per_100g": 1.9, "carbs_per_100g": 5, 
             "fat_per_100g": 0.3, "fiber_per_100g": 2.0, "food_category": "vegetable"},
            
            # Proteins
            {"name": "chicken breast", "aliases": ["chicken", "grilled chicken", "chicken meat"], 
             "calories_per_100g": 165, "protein_per_100g": 31, "carbs_per_100g": 0, 
             "fat_per_100g": 3.6, "fiber_per_100g": 0, "food_category": "meat"},
            {"name": "salmon", "aliases": ["salmon fillet", "grilled salmon"], 
             "calories_per_100g": 208, "protein_per_100g": 20, "carbs_per_100g": 0, 
             "fat_per_100g": 13, "fiber_per_100g": 0, "food_category": "seafood"},
            {"name": "beef", "aliases": ["steak", "ground beef", "beef steak"], 
             "calories_per_100g": 250, "protein_per_100g": 26, "carbs_per_100g": 0, 
             "fat_per_100g": 17, "fiber_per_100g": 0, "food_category": "meat"},
            {"name": "egg", "aliases": ["eggs", "chicken egg", "whole egg"], 
             "calories_per_100g": 155, "protein_per_100g": 13, "carbs_per_100g": 1.1, 
             "fat_per_100g": 11, "fiber_per_100g": 0, "food_category": "protein"},
            {"name": "tofu", "aliases": ["bean curd"], 
             "calories_per_100g": 76, "protein_per_100g": 8, "carbs_per_100g": 1.9, 
             "fat_per_100g": 4.8, "fiber_per_100g": 0.3, "food_category": "protein"},
            {"name": "pork", "aliases": ["pork chop", "pork meat"], 
             "calories_per_100g": 242, "protein_per_100g": 27, "carbs_per_100g": 0, 
             "fat_per_100g": 14, "fiber_per_100g": 0, "food_category": "meat"},
            {"name": "turkey", "aliases": ["turkey breast", "turkey meat"], 
             "calories_per_100g": 135, "protein_per_100g": 30, "carbs_per_100g": 0, 
             "fat_per_100g": 1.5, "fiber_per_100g": 0, "food_category": "meat"},
            {"name": "shrimp", "aliases": ["prawns", "prawn"], 
             "calories_per_100g": 99, "protein_per_100g": 24, "carbs_per_100g": 0.2, 
             "fat_per_100g": 0.3, "fiber_per_100g": 0, "food_category": "seafood"},
            
            # Grains & Carbs
            {"name": "white rice", "aliases": ["rice", "cooked rice", "steamed rice"], 
             "calories_per_100g": 130, "protein_per_100g": 2.7, "carbs_per_100g": 28, 
             "fat_per_100g": 0.3, "fiber_per_100g": 0.4, "food_category": "grain"},
            {"name": "brown rice", "aliases": ["whole grain rice"], 
             "calories_per_100g": 111, "protein_per_100g": 2.6, "carbs_per_100g": 23, 
             "fat_per_100g": 0.9, "fiber_per_100g": 1.8, "food_category": "grain"},
            {"name": "white bread", "aliases": ["bread", "bread slice"], 
             "calories_per_100g": 265, "protein_per_100g": 9, "carbs_per_100g": 49, 
             "fat_per_100g": 3.2, "fiber_per_100g": 2.7, "food_category": "grain"},
            {"name": "pasta", "aliases": ["cooked pasta", "spaghetti"], 
             "calories_per_100g": 158, "protein_per_100g": 5.8, "carbs_per_100g": 31, 
             "fat_per_100g": 0.9, "fiber_per_100g": 1.8, "food_category": "grain"},
            {"name": "oatmeal", "aliases": ["oats", "cooked oatmeal"], 
             "calories_per_100g": 68, "protein_per_100g": 2.4, "carbs_per_100g": 12, 
             "fat_per_100g": 1.4, "fiber_per_100g": 1.7, "food_category": "grain"},
            {"name": "quinoa", "aliases": ["cooked quinoa"], 
             "calories_per_100g": 120, "protein_per_100g": 4.4, "carbs_per_100g": 21, 
             "fat_per_100g": 1.9, "fiber_per_100g": 2.8, "food_category": "grain"},
            
            # Dairy
            {"name": "milk", "aliases": ["whole milk", "cow milk"], 
             "calories_per_100g": 61, "protein_per_100g": 3.2, "carbs_per_100g": 4.8, 
             "fat_per_100g": 3.3, "fiber_per_100g": 0, "food_category": "dairy"},
            {"name": "cheddar cheese", "aliases": ["cheese", "cheddar"], 
             "calories_per_100g": 403, "protein_per_100g": 25, "carbs_per_100g": 1.3, 
             "fat_per_100g": 33, "fiber_per_100g": 0, "food_category": "dairy"},
            {"name": "yogurt", "aliases": ["plain yogurt", "greek yogurt"], 
             "calories_per_100g": 59, "protein_per_100g": 10, "carbs_per_100g": 3.6, 
             "fat_per_100g": 0.4, "fiber_per_100g": 0, "food_category": "dairy"},
            {"name": "butter", "aliases": [], 
             "calories_per_100g": 717, "protein_per_100g": 0.9, "carbs_per_100g": 0.1, 
             "fat_per_100g": 81, "fiber_per_100g": 0, "food_category": "dairy"},
            
            # Nuts & Seeds
            {"name": "almond", "aliases": ["almonds"], 
             "calories_per_100g": 579, "protein_per_100g": 21, "carbs_per_100g": 22, 
             "fat_per_100g": 50, "fiber_per_100g": 12.5, "food_category": "nut"},
            {"name": "peanut", "aliases": ["peanuts"], 
             "calories_per_100g": 567, "protein_per_100g": 26, "carbs_per_100g": 16, 
             "fat_per_100g": 49, "fiber_per_100g": 8.5, "food_category": "nut"},
            {"name": "walnut", "aliases": ["walnuts"], 
             "calories_per_100g": 654, "protein_per_100g": 15, "carbs_per_100g": 14, 
             "fat_per_100g": 65, "fiber_per_100g": 6.7, "food_category": "nut"},
            
            # Snacks & Other
            {"name": "chocolate", "aliases": ["chocolate bar", "dark chocolate"], 
             "calories_per_100g": 546, "protein_per_100g": 5, "carbs_per_100g": 61, 
             "fat_per_100g": 31, "fiber_per_100g": 7, "food_category": "snack"},
            {"name": "honey", "aliases": [], 
             "calories_per_100g": 304, "protein_per_100g": 0.3, "carbs_per_100g": 82, 
             "fat_per_100g": 0, "fiber_per_100g": 0.2, "food_category": "sweetener"},
        ]
        
        for food_data in foods:
            FoodNutrition.objects.create(**food_data)
        
        self.stdout.write(self.style.SUCCESS(f'  Loaded {len(foods)} food items'))
    
    def load_shipping_carriers(self):
        """Load shipping carrier rate data"""
        self.stdout.write('Loading shipping carrier data...')
        
        carriers = [
            # USPS
            {"name": "USPS", "service_type": "First Class", "base_rate": 3.50, 
             "rate_per_kg": 2.00, "max_weight_kg": 0.45, "volumetric_divisor": 5000, 
             "is_international": False, "is_active": True},
            {"name": "USPS", "service_type": "Priority Mail", "base_rate": 7.50, 
             "rate_per_kg": 3.50, "max_weight_kg": 31.5, "volumetric_divisor": 5000, 
             "is_international": False, "is_active": True},
            {"name": "USPS", "service_type": "Priority Mail Express", "base_rate": 25.00, 
             "rate_per_kg": 8.00, "max_weight_kg": 31.5, "volumetric_divisor": 5000, 
             "is_international": False, "is_active": True},
            
            # FedEx
            {"name": "FedEx", "service_type": "Ground", "base_rate": 8.00, 
             "rate_per_kg": 3.00, "max_weight_kg": 68, "volumetric_divisor": 5000, 
             "is_international": False, "is_active": True},
            {"name": "FedEx", "service_type": "2-Day", "base_rate": 15.00, 
             "rate_per_kg": 6.00, "max_weight_kg": 68, "volumetric_divisor": 5000, 
             "is_international": False, "is_active": True},
            {"name": "FedEx", "service_type": "Overnight", "base_rate": 30.00, 
             "rate_per_kg": 12.00, "max_weight_kg": 68, "volumetric_divisor": 5000, 
             "is_international": False, "is_active": True},
            
            # UPS
            {"name": "UPS", "service_type": "Ground", "base_rate": 8.50, 
             "rate_per_kg": 3.25, "max_weight_kg": 68, "volumetric_divisor": 5000, 
             "is_international": False, "is_active": True},
            {"name": "UPS", "service_type": "3-Day Select", "base_rate": 12.00, 
             "rate_per_kg": 5.00, "max_weight_kg": 68, "volumetric_divisor": 5000, 
             "is_international": False, "is_active": True},
            {"name": "UPS", "service_type": "2-Day Air", "base_rate": 18.00, 
             "rate_per_kg": 7.00, "max_weight_kg": 68, "volumetric_divisor": 5000, 
             "is_international": False, "is_active": True},
            {"name": "UPS", "service_type": "Next Day Air", "base_rate": 32.00, 
             "rate_per_kg": 13.00, "max_weight_kg": 68, "volumetric_divisor": 5000, 
             "is_international": False, "is_active": True},
            
            # DHL International
            {"name": "DHL", "service_type": "Express Worldwide", "base_rate": 40.00, 
             "rate_per_kg": 15.00, "max_weight_kg": 300, "volumetric_divisor": 5000, 
             "is_international": True, "is_active": True},
        ]
        
        for carrier_data in carriers:
            ShippingCarrier.objects.create(**carrier_data)
        
        self.stdout.write(self.style.SUCCESS(f'  Loaded {len(carriers)} shipping carriers'))
    
    def load_breed_references(self):
        """Load pet breed reference data"""
        self.stdout.write('Loading pet breed data...')
        
        breeds = [
            # Dogs
            {"species": "dog", "breed": "Labrador Retriever", "aliases": ["lab", "labrador"], 
             "adult_min_kg": 25, "adult_max_kg": 36, "underweight_threshold": 0.85, 
             "overweight_threshold": 1.15, "description": "Friendly, active, and outgoing"},
            {"species": "dog", "breed": "German Shepherd", "aliases": ["gsd", "shepherd"], 
             "adult_min_kg": 22, "adult_max_kg": 40, "underweight_threshold": 0.85, 
             "overweight_threshold": 1.15, "description": "Confident, courageous, and smart"},
            {"species": "dog", "breed": "Golden Retriever", "aliases": ["golden"], 
             "adult_min_kg": 25, "adult_max_kg": 34, "underweight_threshold": 0.85, 
             "overweight_threshold": 1.15, "description": "Friendly, intelligent, and devoted"},
            {"species": "dog", "breed": "Bulldog", "aliases": ["english bulldog"], 
             "adult_min_kg": 18, "adult_max_kg": 25, "underweight_threshold": 0.85, 
             "overweight_threshold": 1.15, "description": "Calm, courageous, and friendly"},
            {"species": "dog", "breed": "Beagle", "aliases": [], 
             "adult_min_kg": 9, "adult_max_kg": 11, "underweight_threshold": 0.85, 
             "overweight_threshold": 1.15, "description": "Merry, friendly, and curious"},
            {"species": "dog", "breed": "Poodle", "aliases": ["standard poodle"], 
             "adult_min_kg": 20, "adult_max_kg": 32, "underweight_threshold": 0.85, 
             "overweight_threshold": 1.15, "description": "Active, proud, and very smart"},
            {"species": "dog", "breed": "Rottweiler", "aliases": ["rottie"], 
             "adult_min_kg": 35, "adult_max_kg": 60, "underweight_threshold": 0.85, 
             "overweight_threshold": 1.15, "description": "Loyal, loving, and confident"},
            {"species": "dog", "breed": "Yorkshire Terrier", "aliases": ["yorkie"], 
             "adult_min_kg": 2, "adult_max_kg": 3.5, "underweight_threshold": 0.85, 
             "overweight_threshold": 1.15, "description": "Affectionate, sprightly, and tomboyish"},
            {"species": "dog", "breed": "Boxer", "aliases": [], 
             "adult_min_kg": 25, "adult_max_kg": 32, "underweight_threshold": 0.85, 
             "overweight_threshold": 1.15, "description": "Fun-loving, bright, and active"},
            {"species": "dog", "breed": "Dachshund", "aliases": ["wiener dog"], 
             "adult_min_kg": 7, "adult_max_kg": 15, "underweight_threshold": 0.85, 
             "overweight_threshold": 1.15, "description": "Clever, lively, and courageous"},
            {"species": "dog", "breed": "Siberian Husky", "aliases": ["husky"], 
             "adult_min_kg": 16, "adult_max_kg": 27, "underweight_threshold": 0.85, 
             "overweight_threshold": 1.15, "description": "Loyal, mischievous, and outgoing"},
            {"species": "dog", "breed": "Chihuahua", "aliases": [], 
             "adult_min_kg": 1.5, "adult_max_kg": 3, "underweight_threshold": 0.85, 
             "overweight_threshold": 1.15, "description": "Charming, graceful, and sassy"},
            {"species": "dog", "breed": "Pomeranian", "aliases": ["pom"], 
             "adult_min_kg": 1.9, "adult_max_kg": 3.5, "underweight_threshold": 0.85, 
             "overweight_threshold": 1.15, "description": "Inquisitive, bold, and lively"},
            {"species": "dog", "breed": "Shih Tzu", "aliases": [], 
             "adult_min_kg": 4, "adult_max_kg": 7.2, "underweight_threshold": 0.85, 
             "overweight_threshold": 1.15, "description": "Affectionate, playful, and outgoing"},
            {"species": "dog", "breed": "Border Collie", "aliases": ["collie"], 
             "adult_min_kg": 14, "adult_max_kg": 20, "underweight_threshold": 0.85, 
             "overweight_threshold": 1.15, "description": "Affectionate, smart, and energetic"},
            
            # Cats
            {"species": "cat", "breed": "Persian", "aliases": ["persian cat"], 
             "adult_min_kg": 3, "adult_max_kg": 5.5, "underweight_threshold": 0.85, 
             "overweight_threshold": 1.15, "description": "Sweet, gentle, and calm"},
            {"species": "cat", "breed": "Maine Coon", "aliases": ["maine coon cat"], 
             "adult_min_kg": 5, "adult_max_kg": 11, "underweight_threshold": 0.85, 
             "overweight_threshold": 1.15, "description": "Gentle, friendly, and sociable"},
            {"species": "cat", "breed": "Siamese", "aliases": ["siamese cat"], 
             "adult_min_kg": 2.5, "adult_max_kg": 4.5, "underweight_threshold": 0.85, 
             "overweight_threshold": 1.15, "description": "Social, intelligent, and vocal"},
            {"species": "cat", "breed": "Ragdoll", "aliases": ["ragdoll cat"], 
             "adult_min_kg": 4.5, "adult_max_kg": 9, "underweight_threshold": 0.85, 
             "overweight_threshold": 1.15, "description": "Docile, calm, and affectionate"},
            {"species": "cat", "breed": "British Shorthair", "aliases": ["british cat"], 
             "adult_min_kg": 3.5, "adult_max_kg": 7, "underweight_threshold": 0.85, 
             "overweight_threshold": 1.15, "description": "Easygoing, calm, and loyal"},
            {"species": "cat", "breed": "Bengal", "aliases": ["bengal cat"], 
             "adult_min_kg": 4, "adult_max_kg": 7, "underweight_threshold": 0.85, 
             "overweight_threshold": 1.15, "description": "Confident, active, and curious"},
            {"species": "cat", "breed": "Sphynx", "aliases": ["hairless cat"], 
             "adult_min_kg": 3, "adult_max_kg": 5, "underweight_threshold": 0.85, 
             "overweight_threshold": 1.15, "description": "Loyal, social, and playful"},
            {"species": "cat", "breed": "Scottish Fold", "aliases": [], 
             "adult_min_kg": 2.7, "adult_max_kg": 6, "underweight_threshold": 0.85, 
             "overweight_threshold": 1.15, "description": "Sweet, calm, and adaptable"},
            {"species": "cat", "breed": "Abyssinian", "aliases": ["abyssinian cat"], 
             "adult_min_kg": 3.5, "adult_max_kg": 5.5, "underweight_threshold": 0.85, 
             "overweight_threshold": 1.15, "description": "Active, social, and intelligent"},
            {"species": "cat", "breed": "Russian Blue", "aliases": [], 
             "adult_min_kg": 3, "adult_max_kg": 5.5, "underweight_threshold": 0.85, 
             "overweight_threshold": 1.15, "description": "Gentle, quiet, and reserved"},
        ]
        
        for breed_data in breeds:
            BreedReference.objects.create(**breed_data)
        
        self.stdout.write(self.style.SUCCESS(f'  Loaded {len(breeds)} pet breeds'))
    
    def load_bmi_categories(self):
        """Load BMI category reference data"""
        self.stdout.write('Loading BMI category data...')
        
        categories = [
            {
                "name": "Underweight",
                "min_bmi": 0,
                "max_bmi": 18.4,
                "description": "Below normal weight range",
                "recommendation": "Consider consulting a healthcare provider about healthy weight gain strategies. Focus on nutrient-dense foods and strength training.",
                "color_code": "#3b82f6"  # blue
            },
            {
                "name": "Normal",
                "min_bmi": 18.5,
                "max_bmi": 24.9,
                "description": "Healthy weight range",
                "recommendation": "You're in a healthy weight range. Maintain your current lifestyle with balanced nutrition and regular physical activity.",
                "color_code": "#10b981"  # green
            },
            {
                "name": "Overweight",
                "min_bmi": 25.0,
                "max_bmi": 29.9,
                "description": "Above normal weight range",
                "recommendation": "Consider moderate lifestyle changes for optimal health. Focus on balanced nutrition and increased physical activity.",
                "color_code": "#f59e0b"  # orange
            },
            {
                "name": "Obese",
                "min_bmi": 30.0,
                "max_bmi": 999,
                "description": "Significantly above normal weight range",
                "recommendation": "Consulting a healthcare provider is recommended for personalized guidance on weight management and health optimization.",
                "color_code": "#ef4444"  # red
            },
        ]
        
        for category_data in categories:
            BMICategory.objects.create(**category_data)
        
        self.stdout.write(self.style.SUCCESS(f'  Loaded {len(categories)} BMI categories'))

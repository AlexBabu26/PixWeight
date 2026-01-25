from django.contrib import admin
from .models import WeightEstimate

@admin.register(WeightEstimate)
class WeightEstimateAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "value_grams", "confidence", "created_at")
    list_filter = ("created_at",)


#!/usr/bin/env python3
"""Generate PDF document of database schema tables."""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# Schema data: (table_name, [(column, description, constraints, pk_fk), ...])
SCHEMA = [
    ("accounts_profile", [
        ("id", "Auto-increment primary key", "BigAutoField", "PK"),
        ("display_name", "User display name", "VARCHAR(120), blank", ""),
        ("created_at", "Creation timestamp", "DateTimeField, auto", ""),
        ("user_id", "Reference to user", "OneToOne", "FK → auth_user"),
    ]),
    ("auth_user", [
        ("id", "Auto-increment primary key", "BigAutoField", "PK"),
        ("username", "Username", "VARCHAR(150), unique", ""),
        ("password", "Hashed password", "VARCHAR(128)", ""),
        ("first_name", "First name", "VARCHAR(150)", ""),
        ("last_name", "Last name", "VARCHAR(150)", ""),
        ("email", "Email address", "VARCHAR(254)", ""),
        ("is_staff", "Staff status", "Boolean", ""),
        ("is_active", "Active status", "Boolean", ""),
        ("is_superuser", "Superuser status", "Boolean", ""),
        ("date_joined", "Join timestamp", "DateTimeField", ""),
        ("last_login", "Last login timestamp", "DateTimeField, nullable", ""),
    ]),
    ("media_store_uploadedimage", [
        ("id", "UUID primary key", "UUIDField, editable=False", "PK"),
        ("image", "Image file path", "ImageField", ""),
        ("original_filename", "Original filename", "VARCHAR(255), blank", ""),
        ("size_bytes", "File size in bytes", "PositiveIntegerField", ""),
        ("mime_type", "MIME type", "VARCHAR(64), blank", ""),
        ("created_at", "Creation timestamp", "DateTimeField, auto", ""),
        ("uploaded_by_id", "Uploading user", "ForeignKey", "FK → auth_user"),
    ]),
    ("estimation_sessions_estimationsession", [
        ("id", "UUID primary key", "UUIDField, editable=False", "PK"),
        ("object_label", "Identified object label", "VARCHAR(200), blank", ""),
        ("object_summary", "Object summary", "TextField, blank", ""),
        ("object_json", "Object metadata JSON", "JSONField", ""),
        ("status", "Session status", "VARCHAR(32), choices", ""),
        ("created_at", "Creation timestamp", "DateTimeField, auto", ""),
        ("updated_at", "Last update timestamp", "DateTimeField, auto", ""),
        ("image_id", "Reference to uploaded image", "ForeignKey", "FK → media_store_uploadedimage"),
        ("user_id", "Session owner", "ForeignKey", "FK → auth_user"),
    ]),
    ("estimation_sessions_question", [
        ("id", "UUID primary key", "UUIDField, editable=False", "PK"),
        ("order", "Display order", "PositiveIntegerField", ""),
        ("text", "Question text", "TextField", ""),
        ("answer_type", "Type (text, number, boolean, select)", "VARCHAR(16), choices", ""),
        ("unit", "Unit of measurement", "VARCHAR(32), blank", ""),
        ("options", "Options for select type", "JSONField", ""),
        ("required", "Whether required", "BooleanField", ""),
        ("session_id", "Parent session", "ForeignKey", "FK → estimation_sessions_estimationsession"),
    ]),
    ("estimation_sessions_answer", [
        ("id", "UUID primary key", "UUIDField, editable=False", "PK"),
        ("value_text", "Text answer", "TextField, blank", ""),
        ("value_number", "Numeric answer", "FloatField, nullable", ""),
        ("value_boolean", "Boolean answer", "BooleanField, nullable", ""),
        ("value_json", "Structured answer", "JSONField", ""),
        ("created_at", "Creation timestamp", "DateTimeField, auto", ""),
        ("session_id", "Parent session", "ForeignKey", "FK → estimation_sessions_estimationsession"),
        ("question_id", "Related question", "ForeignKey", "FK → estimation_sessions_question"),
    ]),
    ("estimates_weightestimate", [
        ("id", "UUID primary key", "UUIDField, editable=False", "PK"),
        ("value_grams", "Estimated weight (g)", "FloatField", ""),
        ("min_grams", "Min weight (g)", "FloatField", ""),
        ("max_grams", "Max weight (g)", "FloatField", ""),
        ("confidence", "Confidence score", "FloatField, default 0.3", ""),
        ("unit_display", "Display unit", "VARCHAR(16), default 'g'", ""),
        ("rationale", "Estimation rationale", "TextField, blank", ""),
        ("raw_json", "Raw model output", "JSONField", ""),
        ("category", "food/package/pet/person/general", "VARCHAR(20), choices", ""),
        ("category_metadata", "Category-specific data", "JSONField", ""),
        ("created_at", "Creation timestamp", "DateTimeField, auto", ""),
        ("session_id", "Parent session", "OneToOne", "FK → estimation_sessions_estimationsession"),
    ]),
    ("estimates_foodnutrition", [
        ("id", "Auto-increment primary key", "BigAutoField", "PK"),
        ("name", "Food name", "VARCHAR(100), unique", ""),
        ("aliases", "Alternative names", "JSONField", ""),
        ("calories_per_100g", "Calories per 100g", "FloatField", ""),
        ("protein_per_100g", "Protein per 100g", "FloatField", ""),
        ("carbs_per_100g", "Carbs per 100g", "FloatField", ""),
        ("fat_per_100g", "Fat per 100g", "FloatField", ""),
        ("fiber_per_100g", "Fiber per 100g", "FloatField", ""),
        ("food_category", "fruit, vegetable, meat, etc.", "VARCHAR(50), blank", ""),
        ("created_at", "Creation timestamp", "DateTimeField, auto", ""),
    ]),
    ("estimates_foodestimate", [
        ("id", "Auto-increment primary key", "BigAutoField", "PK"),
        ("estimated_calories", "Estimated calories", "FloatField", ""),
        ("estimated_protein", "Estimated protein", "FloatField", ""),
        ("estimated_carbs", "Estimated carbs", "FloatField", ""),
        ("estimated_fat", "Estimated fat", "FloatField", ""),
        ("estimated_fiber", "Estimated fiber", "FloatField", ""),
        ("is_cooked", "Cooked or raw", "BooleanField", ""),
        ("portion_status", "whole, partial, etc.", "VARCHAR(50), blank", ""),
        ("created_at", "Creation timestamp", "DateTimeField, auto", ""),
        ("estimate_id", "Parent weight estimate", "OneToOne", "FK → estimates_weightestimate"),
        ("food_reference_id", "Matched food reference", "ForeignKey, nullable", "FK → estimates_foodnutrition"),
    ]),
    ("estimates_shippingcarrier", [
        ("id", "Auto-increment primary key", "BigAutoField", "PK"),
        ("name", "Carrier name", "VARCHAR(100)", ""),
        ("service_type", "Ground, Express, etc.", "VARCHAR(50)", ""),
        ("base_rate", "Base shipping rate", "Decimal(10,2)", ""),
        ("rate_per_kg", "Rate per kg", "Decimal(10,2)", ""),
        ("max_weight_kg", "Max weight (kg)", "FloatField", ""),
        ("volumetric_divisor", "Volumetric weight divisor", "IntegerField, default 5000", ""),
        ("is_international", "International service", "BooleanField", ""),
        ("is_active", "Active flag", "BooleanField", ""),
        ("created_at", "Creation timestamp", "DateTimeField, auto", ""),
    ]),
    ("estimates_packageestimate", [
        ("id", "Auto-increment primary key", "BigAutoField", "PK"),
        ("length_cm", "Length (cm)", "FloatField, nullable", ""),
        ("width_cm", "Width (cm)", "FloatField, nullable", ""),
        ("height_cm", "Height (cm)", "FloatField, nullable", ""),
        ("volumetric_weight_g", "Volumetric weight (g)", "FloatField, nullable", ""),
        ("chargeable_weight_g", "Chargeable weight (g)", "FloatField", ""),
        ("estimated_shipping_costs", "Carrier costs", "JSONField", ""),
        ("is_fragile", "Fragile flag", "BooleanField", ""),
        ("destination_type", "domestic, international", "VARCHAR(20), blank", ""),
        ("created_at", "Creation timestamp", "DateTimeField, auto", ""),
        ("estimate_id", "Parent weight estimate", "OneToOne", "FK → estimates_weightestimate"),
    ]),
    ("estimates_breedreference", [
        ("id", "Auto-increment primary key", "BigAutoField", "PK"),
        ("species", "dog, cat, rabbit, etc.", "VARCHAR(50)", ""),
        ("breed", "Breed name", "VARCHAR(100)", ""),
        ("aliases", "Alternative breed names", "JSONField", ""),
        ("puppy_min_kg", "Puppy min weight (kg)", "FloatField, nullable", ""),
        ("puppy_max_kg", "Puppy max weight (kg)", "FloatField, nullable", ""),
        ("adult_min_kg", "Adult min weight (kg)", "FloatField", ""),
        ("adult_max_kg", "Adult max weight (kg)", "FloatField", ""),
        ("senior_min_kg", "Senior min weight (kg)", "FloatField, nullable", ""),
        ("senior_max_kg", "Senior max weight (kg)", "FloatField, nullable", ""),
        ("underweight_threshold", "Underweight threshold", "FloatField, default 0.85", ""),
        ("overweight_threshold", "Overweight threshold", "FloatField, default 1.15", ""),
        ("description", "Breed description", "TextField, blank", ""),
        ("created_at", "Creation timestamp", "DateTimeField, auto", ""),
    ]),
    ("estimates_petestimate", [
        ("id", "Auto-increment primary key", "BigAutoField", "PK"),
        ("species", "Pet species", "VARCHAR(50)", ""),
        ("breed", "Breed name", "VARCHAR(100), blank", ""),
        ("age_category", "puppy, adult, senior", "VARCHAR(20), blank", ""),
        ("gender", "Gender", "VARCHAR(10), blank", ""),
        ("is_neutered", "Neutered status", "BooleanField, nullable", ""),
        ("health_status", "underweight, healthy, overweight", "VARCHAR(20), blank", ""),
        ("ideal_weight_min", "Ideal min weight (kg)", "FloatField, nullable", ""),
        ("ideal_weight_max", "Ideal max weight (kg)", "FloatField, nullable", ""),
        ("weight_recommendation", "Recommendation text", "TextField, blank", ""),
        ("created_at", "Creation timestamp", "DateTimeField, auto", ""),
        ("estimate_id", "Parent weight estimate", "OneToOne", "FK → estimates_weightestimate"),
        ("breed_reference_id", "Matched breed reference", "ForeignKey, nullable", "FK → estimates_breedreference"),
    ]),
    ("estimates_bmicategory", [
        ("id", "Auto-increment primary key", "BigAutoField", "PK"),
        ("name", "Category name", "VARCHAR(20), unique", ""),
        ("min_bmi", "Min BMI", "FloatField", ""),
        ("max_bmi", "Max BMI", "FloatField", ""),
        ("description", "Category description", "TextField", ""),
        ("recommendation", "Health recommendation", "TextField", ""),
        ("color_code", "Display color", "VARCHAR(20), blank", ""),
        ("created_at", "Creation timestamp", "DateTimeField, auto", ""),
    ]),
    ("estimates_bodycompositionestimate", [
        ("id", "Auto-increment primary key", "BigAutoField", "PK"),
        ("height_cm", "Height (cm)", "FloatField", ""),
        ("age", "Age (years)", "IntegerField, nullable", ""),
        ("gender", "Gender", "VARCHAR(20), blank", ""),
        ("activity_level", "Activity level", "VARCHAR(50), blank", ""),
        ("bmi", "Calculated BMI", "FloatField", ""),
        ("bmi_category", "BMI category name", "VARCHAR(20)", ""),
        ("ideal_weight_min_kg", "Ideal min weight (kg)", "FloatField", ""),
        ("ideal_weight_max_kg", "Ideal max weight (kg)", "FloatField", ""),
        ("body_fat_estimate", "Body fat %", "FloatField, nullable", ""),
        ("lean_mass_estimate", "Lean mass (kg)", "FloatField, nullable", ""),
        ("health_recommendation", "Recommendation text", "TextField, blank", ""),
        ("created_at", "Creation timestamp", "DateTimeField, auto", ""),
        ("estimate_id", "Parent weight estimate", "OneToOne", "FK → estimates_weightestimate"),
        ("bmi_category_ref_id", "BMI category reference", "ForeignKey, nullable", "FK → estimates_bmicategory"),
    ]),
    ("estimates_weightfeedback", [
        ("id", "Auto-increment primary key", "BigAutoField", "PK"),
        ("actual_weight_grams", "Actual weight (g)", "FloatField", ""),
        ("accuracy_rating", "1-5 star rating", "IntegerField, nullable", ""),
        ("user_notes", "User notes", "TextField, blank", ""),
        ("helpful", "Helpful flag", "BooleanField", ""),
        ("error_grams", "Absolute error (g)", "FloatField, nullable", ""),
        ("error_percentage", "Error %", "FloatField, nullable", ""),
        ("created_at", "Creation timestamp", "DateTimeField, auto", ""),
        ("estimate_id", "Parent weight estimate", "OneToOne", "FK → estimates_weightestimate"),
    ]),
]


def main():
    output_path = "docs/database_schema.pdf"
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name="CustomTitle",
        parent=styles["Heading1"],
        fontSize=18,
        spaceAfter=12,
    )
    table_header_style = ParagraphStyle(
        name="TableHeader",
        parent=styles["Heading2"],
        fontSize=12,
        spaceAfter=6,
        spaceBefore=12,
    )

    story = []
    story.append(Paragraph("Database Schema Documentation", title_style))
    story.append(Paragraph("Weight Estimator using Image", styles["Normal"]))
    story.append(Spacer(1, 0.25 * inch))

    for table_name, columns in SCHEMA:
        story.append(Paragraph(table_name, table_header_style))

        # Build table data: header row + data rows
        table_data = [
            ["Column", "Description", "Constraints", "PK / FK"],
        ]
        for col, desc, constraints, pk_fk in columns:
            table_data.append([col, desc, constraints, pk_fk])

        t = Table(table_data, colWidths=[1.4 * inch, 2.2 * inch, 2.0 * inch, 1.4 * inch])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                    ("TOPPADDING", (0, 0), (-1, 0), 8),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 8),
                    ("TOPPADDING", (0, 1), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F2F2")]),
                ]
            )
        )
        story.append(t)
        story.append(Spacer(1, 0.2 * inch))

    doc.build(story)
    print(f"PDF generated: {output_path}")


if __name__ == "__main__":
    main()

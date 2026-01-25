from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from media_store.models import UploadedImage
from estimates.models import (
    WeightEstimate, FoodEstimate, PackageEstimate, 
    PetEstimate, BodyCompositionEstimate, FoodNutrition, BMICategory
)
from estimates.serializers import WeightEstimateSerializer
from estimates.calculations import (
    calculate_nutrition, calculate_shipping_costs,
    assess_pet_health, calculate_bmi_insights, extract_answer_value
)

from .models import EstimationSession, Question, Answer, SessionStatus
from .serializers import (
    SessionSerializer,
    CreateSessionFromImageSerializer,
    SubmitAnswersSerializer,
)
from .services import (
    image_file_to_data_url,
    validate_image_content,
    identify_object_and_questions,
    estimate_weight,
    detect_category,
    LLMError,
    ImageValidationError,
    OpenRouterError,  # Backward compatibility
)

class CreateSessionFromImageAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_scope = "llm"

    def post(self, request):
        ser = CreateSessionFromImageSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        img = get_object_or_404(
            UploadedImage,
            id=ser.validated_data["image_id"],
            uploaded_by=request.user
        )

        user_hint = ser.validated_data.get("user_hint", "")

        try:
            data_url = image_file_to_data_url(img.image.path, mime_type=img.mime_type or "image/jpeg")
            
            # Validate image content before processing
            try:
                validate_image_content(data_url)
            except ImageValidationError as e:
                return Response({"detail": str(e)}, status=400)
            
            llm_out = identify_object_and_questions(data_url, user_hint=user_hint)
        except (LLMError, Exception) as e:
            return Response({"detail": str(e)}, status=502)

        # Extract category from LLM output
        category = llm_out.get("category", "general")
        
        session = EstimationSession.objects.create(
            user=request.user,
            image=img,
            object_label=str(llm_out.get("object_label", "") or "")[:200],
            object_summary=str(llm_out.get("object_summary", "") or ""),
            object_json=llm_out,
            status=SessionStatus.QUESTIONS_ASKED,
        )
        
        # Store category in session metadata for later use
        session.object_json["detected_category"] = category
        session.save()

        questions = llm_out.get("questions", []) or []
        for idx, q in enumerate(questions, start=1):
            Question.objects.create(
                session=session,
                order=idx,
                text=str(q.get("question", "") or "").strip(),
                answer_type=str(q.get("answer_type", "text") or "text").strip(),
                unit=str(q.get("unit", "") or "").strip(),
                options=q.get("options", []) or [],
                required=bool(q.get("required", True)),
            )

        return Response(SessionSerializer(session).data, status=201)

class SessionListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = EstimationSession.objects.filter(user=request.user)
        
        # ============================================
        # SEARCH & FILTERING
        # ============================================
        
        # Search by object label or summary
        search = request.query_params.get("search", "").strip()
        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(object_label__icontains=search) | 
                Q(object_summary__icontains=search)
            )
        
        # Filter by status
        status_filter = request.query_params.get("status", "").strip()
        if status_filter:
            qs = qs.filter(status=status_filter)
        
        # Filter by category (from object_json)
        category_filter = request.query_params.get("category", "").strip()
        if category_filter:
            qs = qs.filter(object_json__detected_category=category_filter)
        
        # Filter by date range
        date_from = request.query_params.get("date_from", "").strip()
        date_to = request.query_params.get("date_to", "").strip()
        
        if date_from:
            try:
                from datetime import datetime
                date_from_obj = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                qs = qs.filter(created_at__gte=date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                from datetime import datetime
                date_to_obj = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                qs = qs.filter(created_at__lte=date_to_obj)
            except ValueError:
                pass
        
        # Sorting
        sort_by = request.query_params.get("sort_by", "date").strip().lower()
        if sort_by == "confidence":
            # Sort by estimate confidence (requires join)
            qs = qs.select_related("estimate").order_by("-estimate__confidence", "-created_at")
        elif sort_by == "weight":
            # Sort by estimate weight
            qs = qs.select_related("estimate").order_by("-estimate__value_grams", "-created_at")
        else:  # Default: date
            qs = qs.order_by("-created_at")
        
        # ============================================
        # STATISTICS CALCULATION
        # ============================================
        
        all_sessions = EstimationSession.objects.filter(user=request.user)
        total_count = all_sessions.count()
        completed_count = all_sessions.filter(status=SessionStatus.ESTIMATED).count()
        pending_count = total_count - completed_count
        
        # Calculate average confidence
        from django.db.models import Avg
        avg_confidence = all_sessions.filter(
            estimate__isnull=False
        ).aggregate(
            avg_conf=Avg("estimate__confidence")
        )["avg_conf"] or 0
        
        # Category breakdown
        category_counts = {}
        for category in ["food", "package", "pet", "person", "general"]:
            count = all_sessions.filter(object_json__detected_category=category).count()
            if count > 0:
                category_counts[category] = count
        
        statistics = {
            "total_sessions": total_count,
            "completed_sessions": completed_count,
            "pending_sessions": pending_count,
            "average_confidence": round(avg_confidence * 100, 1) if avg_confidence else 0,
            "category_breakdown": category_counts,
        }
        
        # Return sessions with statistics
        return Response({
            "sessions": SessionSerializer(qs, many=True).data,
            "statistics": statistics,
        })

class SessionDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, session_id):
        session = get_object_or_404(EstimationSession, id=session_id, user=request.user)
        data = SessionSerializer(session).data

        est = getattr(session, "estimate", None)
        data["estimate"] = WeightEstimateSerializer(est).data if est else None
        return Response(data)

class SubmitAnswersAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_scope = "llm"

    def post(self, request, session_id):
        session = get_object_or_404(EstimationSession, id=session_id, user=request.user)

        ser = SubmitAnswersSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        q_by_id = {str(q.id): q for q in session.questions.all()}

        for item in ser.validated_data["answers"]:
            qid = str(item["question_id"])
            if qid not in q_by_id:
                return Response({"detail": f"Unknown question_id: {qid}"}, status=400)

            q = q_by_id[qid]
            val = item["value"]

            ans, _ = Answer.objects.get_or_create(session=session, question=q)
            ans.value_text = ""
            ans.value_number = None
            ans.value_boolean = None
            ans.value_json = {}

            if q.answer_type == "number":
                try:
                    ans.value_number = float(val)
                except Exception:
                    return Response({"detail": f"Invalid number for question {qid}"}, status=400)
            elif q.answer_type == "boolean":
                # Accept true/false, "true"/"false", 1/0
                if isinstance(val, str):
                    ans.value_boolean = val.strip().lower() in ["true", "1", "yes", "y"]
                else:
                    ans.value_boolean = bool(val)
            elif q.answer_type == "select":
                ans.value_text = str(val)
            else:
                ans.value_text = str(val)

            ans.save()

        session.status = SessionStatus.IN_PROGRESS
        session.save(update_fields=["status", "updated_at"])

        required_qs = session.questions.filter(required=True).count()
        answered_required = Answer.objects.filter(session=session, question__required=True).count()

        if required_qs and answered_required < required_qs:
            return Response(
                {"detail": "Answers saved. More required questions remain.", "session": SessionSerializer(session).data},
                status=200
            )

        if hasattr(session, "estimate"):
            return Response(
                {"detail": "Session already estimated.", "estimate": WeightEstimateSerializer(session.estimate).data},
                status=200
            )

        qa_items = []
        for q in session.questions.all():
            a = Answer.objects.filter(session=session, question=q).first()
            if not a:
                av = None
            elif q.answer_type == "number":
                av = a.value_number
            elif q.answer_type == "boolean":
                av = a.value_boolean
            else:
                av = a.value_text

            qa_items.append({
                "question": q.text,
                "answer_type": q.answer_type,
                "unit": q.unit,
                "answer": av,
                "options": q.options,
                "required": q.required,
            })

        try:
            llm_est = estimate_weight(
                object_label=session.object_label,
                object_summary=session.object_summary,
                qa={"items": qa_items}
            )
        except (LLMError, Exception) as e:
            session.status = SessionStatus.FAILED
            session.save(update_fields=["status", "updated_at"])
            return Response({"detail": str(e)}, status=502)

        grams = llm_est.get("_normalized_grams", {}) or {}
        ew = llm_est.get("estimated_weight", {}) or {}
        
        # Detect category from object label
        category = detect_category(session.object_label)
        if not category:
            category = session.object_json.get("detected_category", "general")

        est = WeightEstimate.objects.create(
            session=session,
            value_grams=float(grams.get("value_g", 0.0) or 0.0),
            min_grams=float(grams.get("min_g", grams.get("value_g", 0.0)) or 0.0),
            max_grams=float(grams.get("max_g", grams.get("value_g", 0.0)) or 0.0),
            confidence=float(llm_est.get("confidence", 0.3) or 0.3),
            unit_display=str(ew.get("unit", "g") or "g"),
            rationale=str(llm_est.get("rationale", "") or "")[:2000],
            raw_json=llm_est,
            category=category,
        )
        
        # ============================================
        # CATEGORY-SPECIFIC CALCULATIONS
        # ============================================
        
        weight_kg = est.value_grams / 1000.0
        
        try:
            if category == "food":
                # Calculate nutrition information
                nutrition_data = calculate_nutrition(
                    weight_grams=est.value_grams,
                    food_name=session.object_label,
                    answers={}  # Could extract cooking status from answers
                )
                
                if nutrition_data.get("found"):
                    food_ref_id = nutrition_data.get("food_reference_id")
                    food_ref = FoodNutrition.objects.filter(id=food_ref_id).first() if food_ref_id else None
                    
                    FoodEstimate.objects.create(
                        estimate=est,
                        food_reference=food_ref,
                        estimated_calories=nutrition_data.get("estimated_calories", 0),
                        estimated_protein=nutrition_data.get("estimated_protein", 0),
                        estimated_carbs=nutrition_data.get("estimated_carbs", 0),
                        estimated_fat=nutrition_data.get("estimated_fat", 0),
                        estimated_fiber=nutrition_data.get("estimated_fiber", 0),
                    )
                    est.category_metadata = nutrition_data
                    est.save(update_fields=["category_metadata"])
                    
            elif category == "package":
                # Extract dimensions from answers
                length_cm = extract_answer_value(qa_items, "length", 0)
                width_cm = extract_answer_value(qa_items, "width", 0)
                height_cm = extract_answer_value(qa_items, "height", 0)
                destination = extract_answer_value(qa_items, "destination", "Domestic")
                
                if length_cm and width_cm and height_cm:
                    shipping_data = calculate_shipping_costs(
                        weight_grams=est.value_grams,
                        dimensions={
                            "length_cm": length_cm,
                            "width_cm": width_cm,
                            "height_cm": height_cm,
                        },
                        destination_type=destination
                    )
                    
                    PackageEstimate.objects.create(
                        estimate=est,
                        length_cm=length_cm,
                        width_cm=width_cm,
                        height_cm=height_cm,
                        volumetric_weight_g=shipping_data.get("volumetric_weight_g"),
                        chargeable_weight_g=shipping_data.get("chargeable_weight_g", est.value_grams),
                        estimated_shipping_costs=shipping_data.get("shipping_costs", {}),
                        destination_type=destination,
                    )
                    est.category_metadata = shipping_data
                    est.save(update_fields=["category_metadata"])
                    
            elif category == "pet":
                # Extract pet details from answers
                breed_name = extract_answer_value(qa_items, "breed", "")
                age_category = extract_answer_value(qa_items, "age", "adult")
                gender = extract_answer_value(qa_items, "gender", "")
                
                # Extract species from object label
                species = "dog"  # default
                if "cat" in session.object_label.lower():
                    species = "cat"
                elif "rabbit" in session.object_label.lower():
                    species = "rabbit"
                
                health_data = assess_pet_health(
                    weight_kg=weight_kg,
                    species=species,
                    breed_name=breed_name,
                    age_category=age_category
                )
                
                if age_category and "puppy" in age_category.lower() or "kitten" in age_category.lower():
                    age_cat = "puppy" if species == "dog" else "kitten"
                elif "senior" in age_category.lower():
                    age_cat = "senior"
                else:
                    age_cat = "adult"
                
                breed_ref_id = health_data.get("breed_reference_id")
                from estimates.models import BreedReference
                breed_ref = BreedReference.objects.filter(id=breed_ref_id).first() if breed_ref_id else None
                
                PetEstimate.objects.create(
                    estimate=est,
                    species=species,
                    breed=breed_name or health_data.get("breed_name", ""),
                    breed_reference=breed_ref,
                    age_category=age_cat,
                    gender=gender,
                    health_status=health_data.get("health_status", "unknown"),
                    ideal_weight_min=health_data.get("ideal_weight_min"),
                    ideal_weight_max=health_data.get("ideal_weight_max"),
                    weight_recommendation=health_data.get("weight_recommendation", ""),
                )
                est.category_metadata = health_data
                est.save(update_fields=["category_metadata"])
                
            elif category == "person":
                # Extract person details from answers
                height_cm = extract_answer_value(qa_items, "height", None)
                age = extract_answer_value(qa_items, "age", None)
                gender = extract_answer_value(qa_items, "gender", None)
                activity = extract_answer_value(qa_items, "activity", None)
                
                if height_cm:
                    bmi_data = calculate_bmi_insights(
                        weight_kg=weight_kg,
                        height_cm=float(height_cm),
                        age=int(age) if age else None,
                        gender=gender,
                        activity_level=activity
                    )
                    
                    bmi_cat_id = bmi_data.get("bmi_category_id")
                    bmi_cat = BMICategory.objects.filter(id=bmi_cat_id).first() if bmi_cat_id else None
                    
                    BodyCompositionEstimate.objects.create(
                        estimate=est,
                        height_cm=float(height_cm),
                        age=int(age) if age else None,
                        gender=gender or "",
                        activity_level=activity or "",
                        bmi=bmi_data.get("bmi", 0),
                        bmi_category=bmi_data.get("bmi_category", ""),
                        bmi_category_ref=bmi_cat,
                        ideal_weight_min_kg=bmi_data.get("ideal_weight_min_kg", 0),
                        ideal_weight_max_kg=bmi_data.get("ideal_weight_max_kg", 0),
                        body_fat_estimate=bmi_data.get("body_fat_estimate"),
                        lean_mass_estimate=bmi_data.get("lean_mass_estimate"),
                        health_recommendation=bmi_data.get("health_recommendation", ""),
                    )
                    est.category_metadata = bmi_data
                    est.save(update_fields=["category_metadata"])
                    
        except Exception as e:
            # Log error but don't fail the estimation
            # Category calculations are optional enhancements
            print(f"Category calculation error: {str(e)}")

        session.status = SessionStatus.ESTIMATED
        session.save(update_fields=["status", "updated_at"])

        return Response({"detail": "Estimated successfully.", "estimate": WeightEstimateSerializer(est).data}, status=200)

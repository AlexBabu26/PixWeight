from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from media_store.models import UploadedImage
from estimates.models import WeightEstimate
from estimates.serializers import WeightEstimateSerializer

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

        session = EstimationSession.objects.create(
            user=request.user,
            image=img,
            object_label=str(llm_out.get("object_label", "") or "")[:200],
            object_summary=str(llm_out.get("object_summary", "") or ""),
            object_json=llm_out,
            status=SessionStatus.QUESTIONS_ASKED,
        )

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
        qs = EstimationSession.objects.filter(user=request.user).order_by("-created_at")
        # Simple pagination-less list; DRF pagination is set globally, but APIView does not auto paginate.
        # Keeping it predictable; frontend can handle. If you want paginator endpoints, switch to ListAPIView.
        return Response(SessionSerializer(qs, many=True).data)

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

        est = WeightEstimate.objects.create(
            session=session,
            value_grams=float(grams.get("value_g", 0.0) or 0.0),
            min_grams=float(grams.get("min_g", grams.get("value_g", 0.0)) or 0.0),
            max_grams=float(grams.get("max_g", grams.get("value_g", 0.0)) or 0.0),
            confidence=float(llm_est.get("confidence", 0.3) or 0.3),
            unit_display=str(ew.get("unit", "g") or "g"),
            rationale=str(llm_est.get("rationale", "") or "")[:2000],
            raw_json=llm_est,
        )

        session.status = SessionStatus.ESTIMATED
        session.save(update_fields=["status", "updated_at"])

        return Response({"detail": "Estimated successfully.", "estimate": WeightEstimateSerializer(est).data}, status=200)

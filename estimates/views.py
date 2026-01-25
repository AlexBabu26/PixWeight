from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import WeightEstimate, WeightFeedback
from .serializers import WeightEstimateSerializer
from .category_serializers import WeightFeedbackSerializer


class EstimateDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, estimate_id):
        est = get_object_or_404(WeightEstimate, id=estimate_id, session__user=request.user)
        return Response(WeightEstimateSerializer(est).data)


class SubmitFeedbackAPIView(APIView):
    """Submit feedback for a weight estimate"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, estimate_id):
        # Get estimate and verify ownership
        est = get_object_or_404(WeightEstimate, id=estimate_id, session__user=request.user)
        
        # Check if feedback already exists
        if hasattr(est, 'feedback'):
            return Response(
                {"detail": "Feedback already submitted for this estimate."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate required fields
        actual_weight = request.data.get("actual_weight_grams")
        if not actual_weight:
            return Response(
                {"detail": "actual_weight_grams is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            actual_weight = float(actual_weight)
            if actual_weight <= 0:
                return Response(
                    {"detail": "actual_weight_grams must be positive."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {"detail": "actual_weight_grams must be a valid number."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create feedback
        feedback = WeightFeedback.objects.create(
            estimate=est,
            actual_weight_grams=actual_weight,
            accuracy_rating=request.data.get("accuracy_rating"),
            user_notes=request.data.get("user_notes", ""),
            helpful=request.data.get("helpful", True),
        )
        
        return Response(
            WeightFeedbackSerializer(feedback).data,
            status=status.HTTP_201_CREATED
        )


class GetFeedbackAPIView(APIView):
    """Get feedback for a weight estimate"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, estimate_id):
        # Get estimate and verify ownership
        est = get_object_or_404(WeightEstimate, id=estimate_id, session__user=request.user)
        
        # Check if feedback exists
        if not hasattr(est, 'feedback'):
            return Response(
                {"detail": "No feedback found for this estimate."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(WeightFeedbackSerializer(est.feedback).data)


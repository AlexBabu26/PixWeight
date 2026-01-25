from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import WeightEstimate
from .serializers import WeightEstimateSerializer

class EstimateDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, estimate_id):
        est = get_object_or_404(WeightEstimate, id=estimate_id, session__user=request.user)
        return Response(WeightEstimateSerializer(est).data)


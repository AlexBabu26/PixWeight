from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer, ProfileSerializer

class RegisterAPIView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

class ProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(ProfileSerializer(request.user.profile).data)

    def patch(self, request):
        profile = request.user.profile
        ser = ProfileSerializer(profile, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)

class ForgotPasswordAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Check if a user exists with the given username or email.
        Returns user info if found to allow password reset.
        """
        identifier = request.data.get('identifier', '').strip()
        
        if not identifier:
            return Response(
                {'error': 'Username or email is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user exists by username or email
        user = None
        try:
            # Try username first
            user = User.objects.get(username=identifier)
        except User.DoesNotExist:
            try:
                # Try email
                user = User.objects.get(email=identifier)
            except User.DoesNotExist:
                pass
        
        if user:
            # Mask email for privacy (show first 2 chars and domain)
            masked_email = None
            if user.email:
                parts = user.email.split('@')
                if len(parts) == 2 and len(parts[0]) > 2:
                    masked_email = f"{parts[0][:2]}***@{parts[1]}"
                elif user.email:
                    masked_email = f"***@{parts[1]}" if len(parts) == 2 else "***"
            
            return Response({
                'success': True,
                'found': True,
                'username': user.username,
                'masked_email': masked_email,
                'message': f'Account found for username: {user.username}'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': True,
                'found': False,
                'message': 'No account found with this username or email.'
            }, status=status.HTTP_200_OK)


class ResetPasswordAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Reset password for a user identified by username.
        Requires username and new password.
        """
        username = request.data.get('username', '').strip()
        new_password = request.data.get('new_password', '')
        confirm_password = request.data.get('confirm_password', '')
        
        # Validation
        if not username:
            return Response(
                {'error': 'Username is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not new_password:
            return Response(
                {'error': 'New password is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(new_password) < 8:
            return Response(
                {'error': 'Password must be at least 8 characters long.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_password != confirm_password:
            return Response(
                {'error': 'Passwords do not match.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find user
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update password
        user.password = make_password(new_password)
        user.save()
        
        return Response({
            'success': True,
            'message': 'Password has been reset successfully. You can now log in with your new password.'
        }, status=status.HTTP_200_OK)


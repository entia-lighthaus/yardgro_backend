from rest_framework import generics, status, serializers, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model

# JWT imports
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegistrationSerializer, UserDetailSerializer, UserUpdateSerializer




User = get_user_model()

@method_decorator(csrf_exempt, name='dispatch')
class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]
    authentication_classes = []  # Disable authentication for registration

    def create(self, request, *args, **kwargs):
        print(f"Incoming registration data: {request.data}")  # Debug print

        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            print(f"Validation errors: {serializer.errors}")  # Debug print
            return Response(
                {
                    "message": "Validation failed",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = serializer.save()
            return Response(
                {
                    "message": "User registered successfully",
                    "user_id": user.id,
                    "username": user.username,
                    "role": user.role
                },
                status=status.HTTP_201_CREATED
            )
        except serializers.ValidationError as ve:
            print(f"Profile creation error: {ve.detail}")  # Debug print
            return Response(
                {
                    "message": "Registration failed",
                    "errors": ve.detail
                },
                status=status.HTTP_409_CONFLICT
            )
        except Exception as e:
            print(f"Unexpected error: {str(e)}")  # Debug print
            return Response(
                {
                    "message": "An unexpected error occurred during registration",
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Login (JWT Token)
class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]


# Refresh token
class TokenRefreshCustomView(TokenRefreshView):
    permission_classes = [AllowAny]


# Logout with token blacklisting
class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Successfully logged out"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# User Detail View
class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'username'



# Update User Profile
class UserProfileUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    http_method_names = ['patch', 'put']  # allow both PATCH and PUT methods

    def get_object(self):
        return self.request.user

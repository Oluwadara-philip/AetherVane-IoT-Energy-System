# AetherVane Accounts App — Views (API Endpoints)
# =================================================
# WHAT IS A VIEW? (plain language)
# A view is the code that actually runs when someone visits a URL.
# It receives the HTTP request, does work (like reading/writing the database),
# and returns an HTTP response (usually JSON).
#
# Think of it as a customer service desk:
#   - The customer sends a request (e.g., "I want to log in")
#   - The view checks their credentials
#   - If correct, it hands them a JWT token (like a day pass)
#   - If wrong, it sends an error message

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import UserRegistrationSerializer, UserSerializer, CustomTokenObtainPairSerializer
from .permissions import IsSuperAdmin


class RegisterView(APIView):
    """
    POST /api/v1/auth/register/
    
    Register a new user account.
    
    Only super_admin can create new users (to prevent anyone from
    creating accounts and accessing energy data).
    """
    permission_classes = [IsSuperAdmin]
    
    def post(self, request):
        # Give the serializer the incoming JSON data
        serializer = UserRegistrationSerializer(data=request.data)
        
        # Check if the data is valid (has all required fields, no duplicate username, etc.)
        if serializer.is_valid():
            # Create the user in the database
            user = serializer.save()
            # Return the user data (without password) as confirmation
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        
        # If data is invalid, return error messages
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    """
    POST /api/v1/auth/login/
    
    Log in with username + password. Returns JWT access + refresh tokens
    plus the user's role and username.
    
    The CustomTokenObtainPairSerializer adds user_role, username, and user_id
    to the response.
    """
    serializer_class = CustomTokenObtainPairSerializer


class CurrentUserView(APIView):
    """
    GET /api/v1/auth/me/
    
    Returns the currently logged-in user's information.
    
    This uses the JWT token to identify who's making the request.
    The frontend calls this on startup to check if the user is still logged in
    and to get their role for showing/hiding UI elements.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class UserListView(APIView):
    """
    GET /api/v1/auth/users/
    
    List all users. Only super_admin can access this.
    Site managers and viewers get a 403 Forbidden response.
    """
    permission_classes = [IsSuperAdmin]
    
    def get(self, request):
        users = User.objects.all().order_by('id')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

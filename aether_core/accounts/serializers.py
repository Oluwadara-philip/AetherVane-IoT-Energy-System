# AetherVane Accounts App — Serializers
# =======================================
# WHAT IS A SERIALIZER? (plain language)
# A serializer converts data between two formats:
#   - Python objects (what Django works with internally)
#   - JSON text (what gets sent over HTTP to/from the frontend and ESP32)
#
# Think of it as a translator:
#   INCOMING: JSON from the request -> Python dict -> validate -> save to DB
#   OUTGOING: DB object -> Python dict -> JSON for the response
#
# A serializer also VALIDATES data — like a bouncer checking IDs at a door.
# If someone sends a registration request without a username, the serializer
# rejects it and returns an error message.

from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for registering new users.
    
    Takes JSON input like:
    {
        "username": "dara",
        "email": "dara@example.com",
        "password": "securepass123",
        "user_role": "site_manager"
    }
    
    And creates a User in the database with the password properly hashed.
    """
    
    # write_only=True means this field is accepted on input but never
    # shown in responses. You don't want passwords appearing in API responses!
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'user_role', 'organization']
        read_only_fields = ['id']  # ID is auto-generated, not set by the user
    
    def create(self, validated_data):
        """
        Create a new user with a hashed password.
        
        We use create_user() instead of create() because create_user()
        automatically hashes the password. If we used create() directly,
        the password would be stored in plain text — a major security flaw.
        """
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # Hash the password securely
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying user information (without password).
    
    Used when listing users or showing the current user's profile.
    Notice: 'password' is NOT in the fields list — it will never be exposed.
    """
    
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'user_role', 'organization', 'organization_name']
        read_only_fields = ['id']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT login serializer that adds the user's role to the token response.
    
    The default JWT login returns: {"access": "...", "refresh": "..."}
    We add: {"access": "...", "refresh": "...", "user_role": "site_manager", "username": "dara"}
    
    This way the frontend knows immediately which role the logged-in user has,
    without making a second API call.
    """
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims (extra information) to the token
        token['user_role'] = user.user_role
        token['username'] = user.username
        return token
    
    def validate(self, attrs):
        """
        Override validate to add user info to the response.
        """
        data = super().validate(attrs)
        # Add user details to the response alongside the tokens
        data['user_role'] = self.user.user_role
        data['username'] = self.user.username
        data['user_id'] = self.user.id
        return data

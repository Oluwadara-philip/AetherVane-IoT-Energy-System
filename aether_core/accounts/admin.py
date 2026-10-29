# AetherVane Accounts App — Admin Registration
# Registers our models with Django's built-in admin panel.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom admin interface for our User model with role field."""
    list_display = ('username', 'email', 'user_role', 'organization', 'is_staff')
    list_filter = ('user_role', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('AetherVane', {'fields': ('user_role', 'organization')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('AetherVane', {'fields': ('user_role', 'organization')}),
    )

# AetherVane Accounts App — Permission Classes
# ==============================================
# WHAT ARE PERMISSIONS? (plain language)
# Permissions are rules that answer: "Is this user ALLOWED to do this action?"
#
# Think of it like a building with different access levels:
#   - The building owner (super_admin) can enter any room
#   - A tenant (site_manager) can only enter their own apartment
#   - A visitor (viewer) can look through windows but can't open doors
#
# In Django REST Framework, a permission class is code that checks
# the request and returns True (allowed) or False (denied) before
# the view even runs.

from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):
    """
    Only allow super_admin users.
    
    Super admins can create organizations, register devices, and manage users.
    They see all data across all sites.
    """
    
    def has_permission(self, request, view):
        # Check if the user is authenticated AND is a super admin
        return bool(request.user and request.user.is_authenticated and request.user.is_super_admin)


class IsSiteManagerOrAbove(BasePermission):
    """
    Allow site_manager and super_admin users.
    
    Site managers can control relays, set thresholds, and manage their sites.
    Viewers cannot.
    """
    
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_super_admin or request.user.is_site_manager)
        )


class IsOwnerOrSuperAdmin(BasePermission):
    """
    Allow users to access only their own data, OR super admins who can see everything.
    
    This is used when a user tries to view or edit a site/device — they can
    only do so if it belongs to them. Super admins bypass this check.
    
    The actual site ownership check happens in the view (queryset filtering),
    but this permission class provides the first layer of defense.
    """
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        # Super admin can access any object
        if request.user.is_super_admin:
            return True
        # For other users, check if the object belongs to their organization
        # This check is a backup; the main filtering happens in the queryset
        if hasattr(obj, 'organization'):
            return obj.organization == request.user.organization
        return False

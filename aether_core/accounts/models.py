# AetherVane Accounts App — Models
# ==================================
# This file defines the database tables for user management.
#
# WHAT IS A MODEL? (plain language)
# A "model" in Django is a Python class that describes a database table.
# Each class becomes a table in MySQL, and each attribute becomes a column.
# Think of it as a blueprint: Django reads this file and builds the actual
# database tables for you automatically (using migrations — explained later).
#
# WHAT THIS FILE DEFINES:
# Our custom User model with a "role" field. This lets us have three types
# of users:
#   - super_admin: Can see and manage everything (all organizations, all sites)
#   - site_manager: Can only see and manage sites assigned to them
#   - viewer: Can only view data, not change anything

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending Django's built-in AbstractUser.
    
    We extend (add to) Django's default user instead of starting from scratch.
    Django's AbstractUser already gives us: username, email, password (hashed),
    first_name, last_name, is_active, is_staff, is_superuser.
    
    We add one important field: user_role.
    
    RBAC = "Role-Based Access Control"
    This means permissions are assigned based on roles, not individual users.
    Like in a company: the manager role can approve expenses, the employee role
    cannot. We don't approve expenses for Bob specifically — we give Bob the
    manager role, and the role carries the permission.
    
    The three roles:
      super_admin   — The system owner. Can create organizations, sites, 
                      register devices, and see everything. Like a building
                      manager who has keys to every apartment.
      site_manager  — Manages one or more specific sites. Can see their sites'
                      data, control relays, but can't see other sites.
                      Like an apartment tenant who only has keys to their unit.
      viewer        — Read-only access. Can see data and charts but cannot
                      change anything or control relays. Like a guest who
                      can look but not touch.
    """
    
    # choices = a list of allowed values. Like a dropdown menu.
    # Each tuple is (value_in_database, human_readable_label).
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('site_manager', 'Site Manager'),
        ('viewer', 'Viewer'),
    ]
    
    # user_role field: stores which role this user has.
    # default='viewer' means new users start with the lowest privilege.
    # This follows the "principle of least privilege" — give users the minimum
    # access they need. You can always grant more, but you can't take back
    # damage done by too much access.
    user_role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='viewer',
    )
    
    # organization: which organization this user belongs to.
    # ForeignKey = a link to another table. This links to the Organization model
    # in the sites app. null=True means a super_admin might not belong to any
    # specific organization (they oversee all of them).
    # We use a string reference 'sites.Organization' to avoid circular imports.
    organization = models.ForeignKey(
        'sites.Organization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
    )
    
    def __str__(self):
        """How this object appears in the admin panel and logs."""
        return "{} ({})".format(self.username, self.get_user_role_display())
    
    @property
    def is_super_admin(self):
        """Shortcut to check if this user is a super admin."""
        return self.user_role == 'super_admin'
    
    @property
    def is_site_manager(self):
        """Shortcut to check if this user is a site manager."""
        return self.user_role == 'site_manager'
    
    @property
    def is_viewer(self):
        """Shortcut to check if this user is a viewer."""
        return self.user_role == 'viewer'

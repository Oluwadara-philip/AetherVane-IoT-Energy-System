# AetherVane Accounts App — URL Routes
# ======================================
# Maps URL paths to the views defined in views.py.
# These are included under /api/v1/auth/ (see aether_core/urls.py)

from django.urls import path
from .views import RegisterView, LoginView, CurrentUserView, UserListView

urlpatterns = [
    # POST /api/v1/auth/register/ — Create a new user (super_admin only)
    path('register/', RegisterView.as_view(), name='register'),
    
    # POST /api/v1/auth/login/ — Log in, get JWT tokens
    path('login/', LoginView.as_view(), name='login'),
    
    # GET /api/v1/auth/me/ — Get current user info
    path('me/', CurrentUserView.as_view(), name='current-user'),
    
    # GET /api/v1/auth/users/ — List all users (super_admin only)
    path('users/', UserListView.as_view(), name='user-list'),
]

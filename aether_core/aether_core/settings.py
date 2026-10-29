# AetherVane Aether Core Engine — Django Project Settings
# ==========================================================
# This file is the "control room" of the Django backend.
# It configures everything: database connection, security, installed apps,
# authentication, and how the API behaves.
#
# WHAT DJANGO IS (plain language):
# Django is a web framework written in Python. A "framework" is like a
# pre-built house structure — the walls, roof, and plumbing are already done.
# You just furnish the rooms. Django handles the boring, repetitive parts
# of building a website (security, database connections, URL routing)
# so you can focus on your actual features.

from pathlib import Path
from decouple import config

# BASE_DIR = the root folder of our Django project.
# Path(__file__) = this settings.py file
# .resolve().parent.parent = go up two folders (from aether_core/aether_core/ to aether_core/)
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Security Settings ---
# SECRET_KEY: A random string Django uses to "sign" things — like putting
# a wax seal on a letter so you know it hasn't been tampered with.
# It's used for passwords, session tokens, etc.
SECRET_KEY = config('SECRET_KEY')

# DEBUG: When True, Django shows detailed error messages (great for development).
# In production, set to False — detailed errors would help attackers.
DEBUG = config('DEBUG', default=True, cast=bool)

# ALLOWED_HOSTS: Which URLs/IPs can serve this site.
# ['*'] means "allow anyone" (fine for development).
ALLOWED_HOSTS = ['*']

# --- Installed Apps ---
# These are all the modules (pieces) that make up our Django project.
# Django needs to know about each one so it can load them.
INSTALLED_APPS = [
    # Django built-in apps (come with Django):
    'django.contrib.admin',           # Admin panel (built-in management interface)
    'django.contrib.auth',            # User authentication (login, users, passwords)
    'django.contrib.contenttypes',    # Tracks which models exist (for permissions)
    'django.contrib.sessions',        # Session management (remembering logged-in users)
    'django.contrib.messages',        # Flash messages (one-time notifications)
    'django.contrib.staticfiles',     # Serves CSS/JS/images during development
    
    # Third-party packages:
    'rest_framework',                 # Django REST Framework (adds API capabilities)
    'rest_framework.authtoken',       # Token authentication (for ESP32 devices)
    'corsheaders',                    # Cross-Origin Resource Sharing (lets Vue.js talk to Django)
    
    # Our apps (we'll create these):
    'accounts',                       # User management, JWT auth, RBAC roles
    'sites',                          # Multi-tenant sites and devices management
    'telemetry',                      # Sensor data ingestion and storage
    'dsl',                            # Dynamic Shedding Logic engine
]

# --- Middleware ---
# Middleware = "layers" that every request passes through, like security
# checkpoints at an airport. Each layer can inspect or modify the request
# before it reaches your code, or the response before it goes back.
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',           # CORS first (before everything)
    'django.middleware.security.SecurityMiddleware',   # Security headers (HTTPS, etc.)
    'django.contrib.sessions.middleware.SessionMiddleware',  # Session handling
    'django.middleware.common.CommonMiddleware',       # Common URL normalization
    'django.middleware.csrf.CsrfViewMiddleware',       # CSRF protection (prevents fake requests)
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Identifies logged-in user
    'django.contrib.messages.middleware.MessageMiddleware',     # Flash messages
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Prevents clickjacking
]

ROOT_URLCONF = 'aether_core.urls'      # Where Django looks for URL routes
WSGI_APPLICATION = 'aether_core.wsgi.application'  # How the web server talks to Django

# --- Templates ---
# Templates are HTML files Django can fill with dynamic data.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# --- Database ---
# We're using MySQL — a popular relational database.
# "Relational" means data is stored in tables (like spreadsheets) that
# can reference each other. For example, a "devices" table has a column
# called "site_id" that points to a row in the "sites" table.
# For development/testing, we can use SQLite (a lightweight file-based database
# that requires no installation). Set DB_ENGINE=sqlite in .env to use it.
# For production, use MySQL (DB_ENGINE=mysql) — it's more powerful for real data.
DB_ENGINE = config('DB_ENGINE', default='mysql')

if DB_ENGINE == 'sqlite':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST'),
            'PORT': config('DB_PORT'),
        }
    }

# --- Password Hashing ---
# How Django stores passwords. It never stores plain text — it "hashes" them.
# Hashing = running the password through a one-way math function that turns
# "mypassword123" into something like "pbkdf2_sha256$870000$abc123...". 
# You can't reverse it back to the original password.
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- Custom User Model ---
# We use a custom User model (in the accounts app) that adds a "role" field.
# This lets us have Super Admin, Site Manager, and Viewer roles.
AUTH_USER_MODEL = 'accounts.User'

# --- REST Framework Settings ---
# These configure how Django REST Framework behaves globally.
REST_FRAMEWORK = {
    # Authentication: how we verify who's making API requests
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # For web users (Vue.js)
        'rest_framework.authentication.TokenAuthentication',           # For ESP32 devices
    ],
    # Permissions: who's allowed to do what
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # Require login by default
    ],
}

# --- JWT Settings ---
# JWT = JSON Web Token. It's how we authenticate users.
# After login, the server gives the user a token (a long string).
# The user sends this token with every API request to prove who they are.
# It's like getting a wristband at a club — show it to get in each time.
#
# ACCESS_TOKEN_LIFETIME: How long the token is valid (15 minutes).
# After it expires, the user uses a "refresh token" to get a new one
# without logging in again.
# REFRESH_TOKEN_LIFETIME: How long the refresh token works (1 day).
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

# --- CORS Settings ---
# CORS (Cross-Origin Resource Sharing) controls which websites can
# talk to our API. The Vue.js frontend runs on a different port
# (e.g., localhost:5173) than Django (localhost:8000), so we need
# to allow it. Without this, the browser blocks the requests.
CORS_ALLOW_ALL_ORIGINS = True  # Allow any origin during development
CORS_ALLOW_CREDENTIALS = True

# --- Internationalization ---
# Settings for language and timezone.
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Shanghai'    # Set to China timezone
USE_I18N = True                # Enable translation
USE_TZ = True                  # Use timezones (store UTC in DB)

# --- Static Files ---
# CSS, JavaScript, and image files served during development.
STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

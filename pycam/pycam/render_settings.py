"""
Production settings for Django deployment on Render.com
"""
from .settings import *  # Import base settings
import os
# Set RENDER environment variable to ensure database configuration works correctly
os.environ['RENDER'] = 'True'


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True  # Keep debug on until we resolve issues

# Allow all hosts temporarily for troubleshooting
ALLOWED_HOSTS = ['*']

# Database connection settings - no need to redefine database config
# since it's already handled in settings.py via DATABASE_URL

# Add database connection middleware
MIDDLEWARE = MIDDLEWARE + [
    'pycam.middleware.DatabaseConnectionMiddleware',
]

# Enable async views
INSTALLED_APPS += ['uvicorn']

# Django Allauth settings
ACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_EMAIL_REQUIRED = False
SOCIALACCOUNT_AUTO_SIGNUP = True

# Make sure login redirects work properly
LOGIN_REDIRECT_URL = '/home/'
LOGIN_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

# Use our custom thread-safe adapters
SOCIALACCOUNT_ADAPTER = 'allauth.socialaccount.adapter.DefaultSocialAccountAdapter'
ACCOUNT_ADAPTER = 'allauth.account.adapter.DefaultAccountAdapter'

# Fix django-allauth threading issues - use JSONSerializer instead of PickleSerializer
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

# CSRF settings for Render - accept all origins temporarily
CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'http://*.onrender.com',
    'https://pycam.onrender.com',
    'http://pycam.onrender.com',
    'https://pyycam.onrender.com',
    'http://pyycam.onrender.com',
]

# Force HTTPS in production
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True

# Temporarily relax some security settings
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Static files settings
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files settings
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Django AllAuth Settings
SITE_ID = 1
SITE_DOMAIN = 'pyycam.onrender.com'
SITE_NAME = 'PyyCam'

# Enable social accounts
SOCIALACCOUNT_ENABLED = True

# Only use Cloudinary if credentials are available
if os.environ.get('CLOUDINARY_CLOUD_NAME') and os.environ.get(
        'CLOUDINARY_API_KEY') and os.environ.get('CLOUDINARY_API_SECRET'):
    # Use cloudinary for storing static and media files
    INSTALLED_APPS += ['cloudinary_storage', 'cloudinary']
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    STATICFILES_STORAGE = 'cloudinary_storage.storage.StaticHashedCloudinaryStorage'

    # Configure Cloudinary
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', ''),
        'API_KEY': os.environ.get('CLOUDINARY_API_KEY', ''),
        'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', ''),
    }
else:
    # If no Cloudinary credentials, use standard file storage
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',  # Set to DEBUG to see all logs
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds

# Social account provider settings

# Redirect URLs
LOGIN_URL = '/'
LOGIN_REDIRECT_URL = 'home'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

# Additional ALLAUTH settings
# These are updated from deprecated settings
ACCOUNT_LOGIN_METHODS = {'username', 'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'none'  # Disable email verification
ACCOUNT_LOGOUT_ON_GET = True  # Bypass the logout confirmation page

# Disable login confirmations and streamline login process
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_SESSION_REMEMBER = True  # Remember user sessions by defaults
ACCOUNT_CONFIRM_EMAIL_ON_GET = True  # Confirm email immediately on click
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = 'home'
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = 'account_login'
ACCOUNT_PASSWORD_RESET_TIMEOUT = 259200  # 3 days in seconds

# Social authentication bypass settings
SOCIALACCOUNT_AUTO_SIGNUP = True  # Directly create user account, no intermediate form
SOCIALACCOUNT_LOGIN_ON_GET = True  # Process social login on GET request (no confirmation page)
ACCOUNT_LOGIN_ON_GET = True  # Process regular login on GET request
SOCIALACCOUNT_FORMS = {}  # Use default forms when necessary

# Additional bypass settings
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'none'
# ACCOUNT_AUTHENTICATION_METHOD is deprecated, replaced by:
# ACCOUNT_LOGIN_METHODS = {'username', 'email'} (already defined above)

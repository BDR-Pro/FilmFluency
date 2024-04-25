"""
Django settings for FilmFluency project.

Generated by 'django-admin startproject' using Django 4.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# settings.py


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('django')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['filmfluency.com', 'www.filmfluency.com', 'localhost']


import os
from django.conf import settings


INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'users',
    'django.contrib.sitemaps',
    'storages',
    'learning',
    'web',
    'api',
    'payment',
    'contact',
    
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
        
]

CORS_ALLOW_ALL_ORIGINS = True 
ROOT_URLCONF = 'FilmFluency.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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


import os
# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
#S3 BUCKET
SECRET_KEY = os.environ.get('SECRET_KEY')
ACCESS_KEY = os.environ.get('ACCESS_KEY')
# Payment

TAP_SECRET_KEY = os.environ.get('TAP_SECRET_KEY')
#DB 
DB_PASS = os.environ.get('DB_PASS')

# EMAIL
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# TMDB

TMDB_API_KEY = os.environ.get('TMDB_API_KEY')

#rdis
RD_PASS = os.environ.get('RD_PASS')


# Create a list of these variables
config_keys = [SECRET_KEY, ACCESS_KEY,RD_PASS, 
                DB_PASS,TAP_SECRET_KEY, EMAIL_HOST_USER, TMDB_API_KEY ,EMAIL_HOST_PASSWORD]

# Check if all elements are not None
is_loaded = all(key is not None for key in config_keys)

if not is_loaded and not DEBUG:
    raise ValueError("Some configuration variables are not set. Please check your environment variables.")

# Database

import os

# Ensure that all your credentials are safe and only referenced here in a secure manner.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'django',  # Database name
        'USER': 'doadmin',  # Database user
        'PASSWORD': DB_PASS,  # Database password
        'HOST': 'dbaas-db-6762329-do-user-16336582-0.c.db.ondigitalocean.com',  # Database host
        'PORT': '25060',  # Database port
        'OPTIONS': {
            'sslmode': 'require',
            'sslrootcert': os.path.join(os.path.dirname(__file__), 'ca-certificate.crt')  # Path to the certificate
        }
    }
}




print("Database loaded successfully")
# ping it
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT 1")
print("Database pinged successfully")


setup = [TMDB_API_KEY,SECRET_KEY, ACCESS_KEY, DB_PASS,RD_PASS]

if all(setup):
    print("All environment variables loaded successfully")
elif DEBUG:
    print("Some environment variables are not set. Please check your environment variables.\n")
    print("TMDB_API_KEY: ", TMDB_API_KEY)
    print("SECRET_KEY: ", SECRET_KEY)
    print("ACCESS_KEY: ", ACCESS_KEY)
    print("DB_PASS: ", DB_PASS)

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators


from api.upload_to_s3 import client_s3

client_s3()

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# settings.py
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"rediss://default:{RD_PASS}@db-redis-fra1-05397-do-user-16336582-0.c.db.ondigitalocean.com:25061/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "username": "default", 
            "Port": "25061",
            "PASSWORD": RD_PASS,
            "SSL": True,  
        },
        "KEY_PREFIX": "example"
    }
}


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]
# Define the static files settings
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Additional places for collecting static files, aside from app 'static' directories
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = ACCESS_KEY
AWS_SECRET_ACCESS_KEY = SECRET_KEY
AWS_STORAGE_BUCKET_NAME = 'filmfluency'
AWS_S3_ENDPOINT_URL = "https://fra1.digitaloceanspaces.com"
CDN_DOMAIN = "https://filmfluency.fra1.cdn.digitaloceanspaces.com"
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
    'ACL': 'public-read'
}
AWS_LOCATION = 'static'

# Static files configuration
STATIC_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.{CDN_DOMAIN}/{AWS_LOCATION}/'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    
JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "Club Admin",

    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "FilmFluency",

    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": "FilmFluency",

    # Logo to use for your site, must be present in static files, used for brand on top left
    "site_logo": "https://filmfluency.fra1.cdn.digitaloceanspaces.com/static/favicon.ico",

    # Logo to use for your site, must be present in static files, used for login form logo (defaults to site_logo)
    "login_logo": "https://filmfluency.fra1.cdn.digitaloceanspaces.com/static/favicon.ico",

    # Logo to use for login form in dark themes (defaults to login_logo)
    "login_logo_dark": None,

    # CSS classes that are applied to the logo above
    "site_logo_classes": "img-circle",

    # Relative path to a favicon for your site, will default to site_logo if absent (ideally 32x32 px)
    "site_icon": None,

    # Welcome text on the login screen
    "welcome_sign": "Welcome to the admin panel",

    # Copyright on the footer
    "copyright": "FilmFluency",

    # List of model admins to search from the search bar, search bar omitted if excluded
    # If you want to use a single search field you dont need to use a list, you can use a simple string 
    "search_model": ["auth.User", "auth.Group"],

    # Field name on user model that contains avatar ImageField/URLField/Charfield or a callable that receives the user
    "user_avatar": None,
    ############
    # Top Menu #
    ############

    # Links to put along the top menu
    "topmenu_links": [

        # Url that gets reversed (Permissions can be added)
        {"name": "Home",  "url": "admin:index", "permissions": ["auth.view_user"]},

        # external url that opens in a new window (Permissions can be added)
        {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},

        # model admin to link to (Permissions checked against model)
        {"model": "auth.User"},

        # App with dropdown menu to all its models pages (Permissions checked against models)
        {"app": "learning"},
    ],

    #############
    # User Menu #
    #############

    # Additional links to include in the user menu on the top right ("app" url type is not allowed)
    "usermenu_links": [
        {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
        {"model": "auth.user"}
    ],

    #############
    # Side Menu #
    #############

    # Whether to display the side menu
    "show_sidebar": True,

    # Whether to aut expand the menu
    "navigation_expanded": True,

    # Hide these apps when generating side menu e.g (auth)
    "hide_apps": [],

    # Hide these models when generating side menu (e.g auth.user)
    "hide_models": [],

    # List of apps (and/or models) to base side menu ordering off of (does not need to contain all apps/models)
    "order_with_respect_to": ["auth", "users", "web", "api", "payment", "contact"],

    # Custom links to append to app groups, keyed on app name
    "custom_links": {
    "learning": [
        {
            "name": "My Unique_Movies",
            "url": "learning:unique_movies",  # Named URL for accessing user-specific courses or learning modules
            "icon": "fas fa-graduation-cap",
            "permissions": ["learning.unique_movies"]
        }
    ],
    "web": [
        {
            "name": "Dashboard",
            "url": "web:dashboard",  # Dashboard URL in the 'web' app
            "icon": "fas fa-tachometer-alt",
            "permissions": ["web.view_dashboard"]
        },
        {
            "name": "All Videos",
            "url": "web:video_list",  # URL for viewing all movies
            "icon": "fas fa-film",
            "permissions": ["web.view_movie"]
        },
        
    ],
    "payment": [
        {
            "name": "Subscription Plans",
            "url": "payment:products",  # URL for viewing different subscription plans
            "icon": "fas fa-credit-card",
            "permissions": ["payment.products"]
        }
    ]
},


    # Custom icons for side menu apps/models See https://fontawesome.com/icons?d=gallery&m=free&v=5.0.0,5.0.1,5.0.10,5.0.11,5.0.12,5.0.13,5.0.2,5.0.3,5.0.4,5.0.5,5.0.6,5.0.7,5.0.8,5.0.9,5.1.0,5.1.1,5.2.0,5.3.0,5.3.1,5.4.0,5.4.1,5.4.2,5.13.0,5.12.0,5.11.2,5.11.1,5.10.0,5.9.0,5.8.2,5.8.1,5.7.2,5.7.1,5.7.0,5.6.3,5.5.0,5.4.2
    # for the full list of 5.13.0 free icon classes
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
    },
    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    #################
    # Related Modal #
    #################
    # Use modals instead of popups
    "related_modal_active": False,

    #############
    # UI Tweaks #
    #############
    # Relative paths to custom CSS/JS scripts (must be present in static files)
    "custom_css": None,
    "custom_js": None,
    # Whether to link font from fonts.googleapis.com (use custom_css to supply font otherwise)
    "use_google_fonts_cdn": True,
    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": False,

    ###############
    # Change view #
    ###############
    # Render out the change view as a single form, or in tabs, current options are
    # - single
    # - horizontal_tabs (default)
    # - vertical_tabs
    # - collapsible
    # - carousel
    "changeform_format": "horizontal_tabs",
    # override change forms on a per modeladmin basis
    "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
    # Add a language dropdown into the admin
    "language_chooser": False,
}

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
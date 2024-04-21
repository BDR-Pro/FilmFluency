"""
Django settings for FilmFluency project.

Generated by 'django-admin startproject' using Django 4.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-7*1q-ook-i)b9_q9^ib(681(m(xs=5q6dv)#!%d48xn$ueiokj'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


import os
from django.conf import settings


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'rest_framework',
    'corsheaders',
    'users',
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
    'web.middleware.BrowserCheckMiddleware'
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

WSGI_APPLICATION = 'FilmFluency.wsgi.application'

import os
TMDB_API_KEY = os.environ.get('TMDB_API_KEY')
# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
#S3 BUCKET
SECRET_KEY = os.environ.get('SECRET_KEY')
ACCESS_KEY = os.environ.get('ACCESS_KEY')
# Payment
PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET')
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID')
PAYPAL_MODE = os.environ.get('PAYPAL_MODE')
COINGATE_API_KEY = os.environ.get('COINGATE_API_KEY')
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


#Twilio
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')

#ipinfo

IPINFO_API_KEY = os.environ.get('IPINFO_API_KEY')

# Create a list of these variables
config_keys = [SECRET_KEY, ACCESS_KEY, 
               COINGATE_API_KEY, DB_PASS,PAYPAL_MODE,TAP_SECRET_KEY, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD,PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET,
        TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER,IPINFO_API_KEY, TMDB_API_KEY]

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
        'NAME': 'defaultdb',  # Database name
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

setup = [TMDB_API_KEY, SECRET_KEY, ACCESS_KEY, DB_PASS]

if all(setup):
    print("All environment variables loaded successfully")
else:
    print("Some environment variables are not set. Please check your environment variables.")

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

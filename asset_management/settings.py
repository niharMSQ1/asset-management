"""
Django settings for asset_management project.

Generated by 'django-admin startproject' using Django 5.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-!r&e9yosa_qip@u%$0^2ar_(wxmp51-n19p-1820hfwckx+@0e'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*","localhost","db45-14-195-33-10.ngrok-free.app"]

CORS_ORIGIN_ALLOW_ALL = True


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    "corsheaders",
    
    'asset_management_tools_integration',

    'chatapp',
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'asset_management.urls'

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

WSGI_APPLICATION = 'asset_management.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SERVICENOW_URL = config('SERVICENOW_URL')
SERVICENOW_USER = config('SERVICENOW_USER')
SERVICENOW_PASSWORD = config('SERVICENOW_PASSWORD')
SERVICENOW_TABLE = "alm_hardware" 


MONGO_URI = config('MONGO_URI')
MONGO_DB_NAME = config('MONGO_DB_NAME')
MONGO_COLLECTION_NAME_FOR_ASSETS_FOR_ASSETS = config('MONGO_COLLECTION_NAME_FOR_ASSETS_FOR_ASSETS')
MONGO_COLLECTION_NAME_FOR_ASSETS_FOR_EMPLOYEES = config('MONGO_COLLECTION_NAME_FOR_ASSETS_FOR_EMPLOYEES')


ACCESS_TOKEN_PY = config("ACCESS_TOKEN_PY")


IBM_MAXIMO_URL = config("IBM_MAXIMO_URL")
IBM_MAXIMO_USERNAME = config("IBM_MAXIMO_USERNAME")
IBM_MAXIMO_PASSWORD = config("IBM_MAXIMO_PASSWORD")


# EZOFFICEINVENTORY
EZOFFICEINVENTORY_URL = config("EZOFFICEINVENTORY_URL")
EZOFFICEINVENTORY_API_SECRET = config("EZOFFICEINVENTORY_API_SECRET")


# ZOHO

ZOHO_REFRESH_TOKEN = ""
ZOHO_CLIENT_ID = config("ZOHO_CLIENT_ID")
ZOHO_CLIENT_SECRET = config("ZOHO_CLIENT_SECRET")
ZOHO_ACCESS_TOKEN = config("ZOHO_ACCESS_TOKEN")

from pathlib import Path
from datetime import timedelta
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-@_xgtip=@)ou&ag0^j2a3(+fk1%8euma@k&rz7&7-@jep5cgo&'

DEBUG = True

ALLOWED_HOSTS = ["*"]

DATABASE_ROUTERS = ['itsmOperations.routers.ServiceNowRouter']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'servicenow',

    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'itsmOperations.urls'

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

WSGI_APPLICATION = 'itsmOperations.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': config('DEFAULT_ENGINE'),
        'NAME': BASE_DIR / config('DEFAULT_NAME'),
    },
    'servicenow': {
        'ENGINE': config('ENGINE'),
        'NAME': config('SERVICENOW_DB_NAME'),
        'USER': config('USER'),
        'PASSWORD': config('PASSWORD'),
        'HOST': config('HOST'),
        'PORT': config('PORT'),
    },
}

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


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True



STATIC_URL = 'static/'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': config('SIGNING_KEY'),
}

SERVICENOW_URL = config('SERVICENOW_URL')
SERVICENOW_USER = config('SERVICENOW_USER')
SERVICENOW_PASSWORD = config('SERVICENOW_PASSWORD')
SERVICENOW_TABLE = "alm_hardware" 


MONGO_URI = config('MONGO_URI')
MONGO_DB_NAME = config('MONGO_DB_NAME')
MONGO_COLLECTION_NAME = config('MONGO_COLLECTION_NAME')


TOKEN_FROM_PHP = config("ACCESS_TOKEN_PY")


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

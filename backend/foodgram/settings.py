from os import getenv
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = getenv('SECRET_KEY')

DEBUG = getenv('DEBUG') == 'True'

ALLOWED_HOSTS = getenv('ALLOWED_HOSTS', 'localhost, 127.0.0.1').split(', ')

CSRF_TRUSTED_ORIGINS = getenv('CSRF_TRUSTED_ORIGINS', 'localhost, 127.0.0.1').split(', ')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'core',
    'recipes',
    'users',

    'django_filters',
    'djoser',
    'rest_framework',
    'rest_framework.authtoken',
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

if DEBUG:
    MIDDLEWARE.append('django_sqlprint_middleware.SqlPrintMiddleware')

ROOT_URLCONF = 'foodgram.urls'

AUTH_USER_MODEL = 'users.User'

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

WSGI_APPLICATION = 'foodgram.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': getenv('POSTGRES_DB', 'django'),
        'USER': getenv('POSTGRES_USER', 'django'),
        'PASSWORD': getenv('POSTGRES_PASSWORD', ''),
        'HOST': getenv('DB_HOST', ''),
        'PORT': getenv('DB_PORT', 5432),
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation'
        '.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
        '.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
        '.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
        '.NumericPasswordValidator',
    },
]


# DRF
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': (
        'rest_framework.pagination.LimitOffsetPagination'
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'EXCEPTION_HANDLER': (
        'api.utils.custom_exception_handler'
    ),
    'PAGE_SIZE': 10,
}

DJOSER = {
    'SERIALIZERS': {
        'user_create': 'api.serializers.UserCustomCreateSerializer',
        'user': 'api.serializers.UserCustomSerializer',
        'current_user': 'api.serializers.UserCustomSerializer',
    },
    'PERMISSIONS': {
        'user': ['rest_framework.permissions.AllowAny'],
        'user_list': ['rest_framework.permissions.AllowAny'],
    },
    'HIDE_USERS': False,
}


# Internationalization
LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'collected_static'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

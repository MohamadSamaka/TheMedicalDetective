"""
Django settings for project project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from dotenv import load_dotenv
from pathlib import Path
from os import getenv

load_dotenv() #loading my .env file

ABSOLUTE_CORE_PARENT_DIR = Path(__file__).resolve().parent.parent.parent
CORE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = getenv('KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = (getenv('DEBUG', "False") == 'TRUE')

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# ALLOWED_HOSTS = []

# Application definition



INSTALLED_APPS = [
    # 'core',
    # 'core.chatbot',
    'daphne',
    'channels',
    'jazzmin',
    # 'admin_argon.apps.AdminArgonConfig',
    # 'admin_corporate.apps.AdminCorporateConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core.core.apps.CoreConfig',
    'core.my_admin.apps.MyadminConfig',
    'core.authentication.apps.AuthenticationConfig',
    'core.healthcare.apps.HealthcareConfig',
    'core.chatbot.apps.ChatbotConfig',
    'core.booking.apps.BookingConfig',
    'core.chatbot_models_manager.apps.ChatbotModelsManagerConfig',
    "bootstrap5",
    "crispy_forms",
    "crispy_bootstrap5",
    "bootstrap_datepicker_plus",
    # "django_flatpickr",
    
]




MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'core.core.src.middlewares.admin_page_redirector.AdminDoctorMiddleware',
    'core.core.src.middlewares.flash_data.FlashDataMiddleware'
]



ROOT_URLCONF = 'core.project.urls'
ASGI_APPLICATION = 'core.core.routing.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
} 

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            CORE_DIR/'templates',
        ],
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

WSGI_APPLICATION = 'core.project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'the-medical-detective',
        'USER': 'root',
        'PASSWORD': '2000',
        'PORT': 3306,
        'HOST': 'localhost',        
    }
}


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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATICFILES_DIRS = [
    CORE_DIR / "statics",
]

AUTH_USER_MODEL = 'my_admin.CustomUser'



EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'mhmdkais20@gmail.com'
# EMAIL_HOST_USER = 'mhmd_dragon1@hotmail.com'
EMAIL_HOST_PASSWORD = 'xhaugdkjklzcuorz'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
# EMAIL_USE_SSL = True

CACHES = {
    "default": {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        "LOCATION": "my_cache_table",
    }
}

CACHE_DEBUG = True

CACHE_BACKEND = "default"


MAX_SEQUENCE_LENGTH = int(getenv('MAX_SEQUENCE_LENGTH'))
VERIFICATION_CODE_TIMEOUT = getenv('VERIFICATION_CODE_TIMEOUT')

#crispy settings
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"


STATIC_ROOT = CORE_DIR / Path('staticfiles')

MEDIA_URL = 'media/'
MEDIA_ROOT = CORE_DIR / MEDIA_URL

PROTECTED_MEDIA_URL = MEDIA_URL / Path("protected")
PROTECTED_MEDIA_ABSOLUTE_URL = MEDIA_ROOT /  Path("protected")


DATASETS_DIR = MEDIA_ROOT / 'datasets'
MODELS_DIR = MEDIA_ROOT / 'models'
TOKENIZERS_DIR = MEDIA_ROOT / 'tokenizers'
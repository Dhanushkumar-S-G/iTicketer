"""
Django settings for iTicketer project.

Generated by 'django-admin startproject' using Django 5.0.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import os
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
IS_PRODUCTION = os.environ.get('IS_PRODUCTION', False)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-i-&^*zfblm6pr60)flm*m4ed1b+b58r6o+buozbvar&5rimoay'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = not IS_PRODUCTION
BASE_URL = 'https://10.1.76.75:6001/' if IS_PRODUCTION else 'http://localhost:8000/'


ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = ['https://jananam.iqubekct.ac.in', 'http://10.1.76.75']

import os
from django.contrib.messages import constants as messages


MESSAGE_TAGS = {
        messages.DEBUG: 'alert-secondary',
        messages.INFO: 'alert-info',
        messages.SUCCESS: 'alert-success',
        messages.WARNING: 'alert-warning',
        messages.ERROR: 'alert-danger',
 }

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATIC_ROOT = 'static_files/'

STATICFILES_DIRS = [
    BASE_DIR / "static",
]
SOCIAL_AUTH_URL_NAMESPACE = 'social'

#Payu

GENERAL_ENTRANCE_FEE = 1

if IS_PRODUCTION:
    
    PAYU_INFO = {
        'merchant_key': "QlHn7C",
        'merchant_salt': "Z8llz8rm",
        'payment_url': 'https://secure.payu.in/_payment',
        'authorization': 'EBLRslXs/+3cUaKuDz7IyZoT2K17aJ8r4kpR0u2aMjo=',
    }
    PAYU_MERCHANT_KEY = "QlHn7C"

else:

    
    PAYU_INFO = {

    'merchant_key': "ZLvSOt",

    'merchant_salt': "TmooTx5BZ3piygXAgjna5vT5I7y4IkRF",

    'payment_url': 'https://test.payu.in/_payment',

    'authorization': 'EBLRslXs/+3cUaKuDz7IyZoT2K17aJ8r4kpR0u2aMjo=',

    }


#Microsoft Authentication
  

# Application definition
SOCIAL_AUTH_JSONFIELD_ENABLED = True
INSTALLED_APPS = [
    'base_app',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap5',
    'social_django',
    'corsheaders',
    'rest_framework',
 
]

MIDDLEWARE = [
    "iTicketer.middleware.MaintenanceMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = 'iTicketer.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # os.path.join(BASE_DIR,'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
           "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = 'iTicketer.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

if IS_PRODUCTION:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('POSTGRES_USER'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
            'HOST': 'postgres',
            'PORT': os.environ.get('POSTGRES_PORT')
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
            'ATOMIC_REQUESTS': True,
        }
    }


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = (
    'social_core.backends.open_id.OpenIdAuth',
    "social_core.backends.azuread.AzureADOAuth2",
    'social_core.backends.azuread_tenant.AzureADTenantOAuth2',
    "django.contrib.auth.backends.ModelBackend",
)


# SOCIAL_AUTH_REQUIRE_POST = True

LOGIN_URL = "/"
LOGIN_REDIRECT_URL = "/dashboard"
LOGOUT_REDIRECT_URL = "/"

SOCIAL_AUTH_AZUREAD_OAUTH2_KEY = '08a2c4f6-1de5-4546-828b-6e2ff08dd3b2'
SOCIAL_AUTH_AZUREAD_OAUTH2_SECRET = 'Dhd8Q~2sDliiGeMPzWFOVuC0TEShEGDblYYX-bMl'
SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_TENANT_ID = '6b8b8296-bdff-4ad8-93ad-84bcbf3842f5'
# SOCIAL_AUTH_AZUREAD_OAUTH2_KEY = "bf89b302-3eb7-42f1-adfd-d4fdbffa1bdd"
# # SOCIAL_AUTH_AZUREAD_OAUTH2_KEY = "bf89b302-3eb7-42f1-adfd-d4fdbffa1bdd"
# SOCIAL_AUTH_AZUREAD_OAUTH2_SECRET = "YKl8Q~p8GE-7CQhregcTEPjRbFHn0~Sqdr6jqaK4"

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)


if DEBUG:
    CELERY_BROKER_URL = "redis://localhost:6379/0"
else:
    CELERY_BROKER_URL = "redis://redis:6379/0"

CELERY_BROKER_TRANSPORT = "redis"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

IS_STAGING = os.environ.get("IS_STAGING") == "TRUE"

CELERY_BEAT_SCHEDULE = {}

WHATSAPP_INSTANCE_KEY = "123"

WHATSAPP_API_IP = "http://10.1.75.42:3333"

MESSAGE_TEMPLATE = "RULES AND REGULATIONS: \n\n NO ENTRY without original Ticket and ID card and acknowledgement Message.\n\n· Everyone should assemble in the ground by 5 PM.\n\n· ZERO TOLERANCE for students found intoxicated or consuming prohibited substances as per Institution policy.\n\n· Everyone should maintain decorum, and if any contrary activities are found, appropriate action will be taken.\n\n· Buses are available only to Gandhipuram at 8.00 PM.\n\n· Once paid, tickets will not be refunded.\n\n· Jananam tickets are only for internal audiences. External audiences are not allowed."

# EARLYBIRD_MAX_BOOKINGS = 800
MAX_BOOKINGS = 2500
# SEATED_MAX_BOOKING = 180 #200
# FIRST_BAY_MAX_BOOKING = 800 #1000
# SECOND_BAY_MAX_BOOKING = 800 #1000

if IS_PRODUCTION:
    import sentry_sdk
    sentry_sdk.init(
        dsn="https://ef74c89d0d39b463b8731eccb79f9176@o389539.ingest.sentry.io/4506503794065408",
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
    )

    SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# settings.py
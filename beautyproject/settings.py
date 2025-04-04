"""
Django settings for beautyproject project.

Generated by 'django-admin startproject' using Django 5.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path

import os




# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# BASE_URL = 'https://mindful-beauty.vercel.app'
BASE_URL = 'https://djangoapp-git-main-mindful-beautys-projects.vercel.app'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-6$_i8h@r7817=w4*7t$lg2)y5=hs*3os!1^gm*n9bp2rswc7ug'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ALLOWED_HOSTS = ['*'] 
ALLOWED_HOSTS = ['mbrestapi-f8cphtgaf7fjdyb0.westcentralus-01.azurewebsites.net','gray-desert-0c1e9470f.4.azurestaticapps.net', 'services.mindfulbeauty.ai','admin.mindfulbeauty.ai', 'mindfulbeauty.ai','localhost', '127.0.0.1']


GOOGLE_MAPS_API_KEY = 'AIzaSyAJMgVfZLEI4QjXqVEQocAmgByXIKgwKwQ'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'beautyapp',
    'serviceapp',
    'rest_framework',
    'corsheaders',
    'storages'
]


DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'



AZURE_ACCOUNT_NAME = 'mbimagestorage'  # Get from Azure Portal
AZURE_ACCOUNT_KEY = 'e/Ld9cY2Jw3Iskw3V6bYlMH67yD7m6XWZvYUHerZmqhV9xdWtAVOPrYo4yxeQrakzK+2jWETGCMa+AStIwkNgQ=='  # Get from Azure Portal
AZURE_CONTAINER = 'mbimages'  # The name of your blob container
AZURE_URL_EXPIRATION_SECS = None  # Optional: set expiry for signed URLs


RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "rzp_live_W6lWHSfydSDFbE")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "BnihE9S930JLq3IvEbSrAo5d")


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'beautyproject.urls'

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

WSGI_APPLICATION = 'beautyproject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'md2025',  # Replace with your PostgreSQL database name
#         'USER': 'mdadmin_2025',       # Replace with your PostgreSQL username
#         'PASSWORD': 'Psd@2025',   # Replace with your PostgreSQL password
#         'HOST': 'md2025.postgres.database.azure.com',           # Replace with your PostgreSQL host, e.g., 'localhost' or an IP address
#         'PORT': '5432',                # Default PostgreSQL port is 5432
#     }
# }


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mdlatestlive',  # Replace with your PostgreSQL database name
        'USER': 'mdlatestlive',       # Replace with your PostgreSQL username
        'PASSWORD': 'Mindfulpsd@2025',   # Replace with your PostgreSQL password
        'HOST': 'mdlatestlive.postgres.database.azure.com',           # Replace with your PostgreSQL host, e.g., 'localhost' or an IP address
        'PORT': '5432',                # Default PostgreSQL port is 5432
    }
}



# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'retool',  # Replace with your PostgreSQL database name
#         'USER': 'retool',       # Replace with your PostgreSQL username
#         'PASSWORD': 'xyn9uXBZfMl5',   # Replace with your PostgreSQL password
#         'HOST': 'ep-jolly-mouse-a65885wt.us-west-2.retooldb.com',           # Replace with your PostgreSQL host, e.g., 'localhost' or an IP address
#         'PORT': '5432',                # Default PostgreSQL port is 5432
#     }
# }

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": "db.sqlite3",
#     }
# }


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
# STATICFILES_DIRS = os.path.join(BASE_DIR, 'static')

# MEDIA_URL = '/media/'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')


MEDIA_URL = f'https://{AZURE_ACCOUNT_NAME}.blob.core.windows.net/{AZURE_CONTAINER}/'
MEDIA_ROOT = None  # No local file storage needed as we're using Azure


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,  # Number of items per page
}


CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://gray-desert-0c1e9470f.4.azurestaticapps.net",
    "https://services.mindfulbeauty.ai",
    "https://admin.mindfulbeauty.ai",
    "https://mindfulbeauty.ai",
    "http://localhost:3000",  # React app running locally
]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'bv-b29.yuvanetworks.in'  # Replace with your SMTP provider
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'anandhi@psdigitise.com'
EMAIL_HOST_PASSWORD = 'aPzozvzhPX'  # Use an App Password if using Gmail
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
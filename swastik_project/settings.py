# from pathlib import Path
# import os

# BASE_DIR = Path(__file__).resolve().parent.parent
# SECRET_KEY = 'swastik-pharmacy-secret-key-change-in-production-2024'
# DEBUG = True
# ALLOWED_HOSTS = ['*']

# INSTALLED_APPS = [
#     'django.contrib.admin',
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.messages',
#     'django.contrib.staticfiles',
#     'pharmacy',
# ]

# MIDDLEWARE = [
#     'django.middleware.security.SecurityMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
# ]

# ROOT_URLCONF = 'swastik_project.urls'

# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#             ],
#         },
#     },
# ]

# WSGI_APPLICATION = 'swastik_project.wsgi.application'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# AUTH_PASSWORD_VALIDATORS = [
#     {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
#     {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
#     {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
#     {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
# ]

# LANGUAGE_CODE = 'en-us'
# TIME_ZONE = 'Asia/Kolkata'
# USE_I18N = True
# USE_TZ = True

# STATIC_URL = '/static/'
# MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / 'media'
# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# # WhatsApp Business API (optional - configure your credentials)
# WHATSAPP_API_TOKEN = os.environ.get('WHATSAPP_API_TOKEN', '')
# WHATSAPP_PHONE_ID = os.environ.get('WHATSAPP_PHONE_ID', '')

# # Pharmacy Info
# PHARMACY_NAME = "Swastik Pharmacy & Surgical Center"
# PHARMACY_OWNER = "Gayatri Upadhyay"
# PHARMACY_DOCTOR = "Dr. Vikash Mishra"
# PHARMACY_PHONE1 = "9450055621"
# PHARMACY_PHONE2 = "8115409504"
# PHARMACY_ADDRESS = "Kanpur, Uttar Pradesh"
# PHARMACY_GSTIN = ""  # Add GSTIN if available

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = 'your-secret-key-change-this'

DEBUG = True

ALLOWED_HOSTS = ['*']  # Render ke liye

# APPLICATIONS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'pharmacy',
]

# MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # static files ke liye
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'swastik_project.urls'

# TEMPLATES
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

WSGI_APPLICATION = 'swastik_project.wsgi.application'

# DATABASE (SQLite - abhi ke liye)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# PASSWORD VALIDATION
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# INTERNATIONAL
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# STATIC FILES (VERY IMPORTANT)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise config
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# MEDIA FILES
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# DEFAULT FIELD
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# OPTIONAL: WhatsApp API
WHATSAPP_API_TOKEN = os.environ.get('WHATSAPP_API_TOKEN', '')
WHATSAPP_PHONE_ID = os.environ.get('WHATSAPP_PHONE_ID', '')

# PHARMACY INFO
PHARMACY_NAME = "Swastik Pharmacy & Surgical Center"
PHARMACY_OWNER = "Gayatri Upadhyay"
PHARMACY_DOCTOR = "Drx. Vikash Mishra"
PHARMACY_PHONE1 = "9450055621"
PHARMACY_PHONE2 = "8115409504"
PHARMACY_ADDRESS = "Gorakhpur, Uttar Pradesh"
PHARMACY_GSTIN = ""
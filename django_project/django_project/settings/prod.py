import os
from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_secret_setting('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': get_secret_setting('DATABASE_NAME'),
        'USER': get_secret_setting('DATABASE_USER'),
        'PASSWORD': get_secret_setting('DATABASE_PASSWORD'),
        'HOST': get_secret_setting('DATABASE_HOST'),
        'PORT': get_secret_setting('DATABASE_PORT'),
    }
}

STATIC_ROOT = 'static'

EMAIL_HOST_USER = get_secret_setting('EMAIL_HOST_USER')
EMAIL_HOST = get_secret_setting('EMAIL_HOST')
EMAIL_HOST_PASSWORD = get_secret_setting('EMAIL_HOST_PASSWORD')
EMAIL_PORT = get_secret_setting('EMAIL_PORT')
EMAIL_USE_TLS = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

DEFAULT_FROM_EMAIL = 'support@overiq.com'
SERVER_EMAIL = 'no-reply@overiq.com'

ADMINS = (
    ('OverIQ', 'infooveriq@gmail.com'),
)

MANAGERS = (
    ('OverIQ', 'manager@overiq.com'),
)
from pathlib import Path
from dotenv import load_dotenv
import os   
load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-fx64mlz4jmzm$p^*&s6k@s6@yz(t1hdhk^9s1)6nh3=bm89590'

DEBUG = True

LOGIN_URL = 'user:login'

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'user',
    'establishment',
    'services',
    'appointment',
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

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'global' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'establishment.context_processors.global_uid',  # Context processor para o UID global
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('SB_NAME'),
        'USER': os.getenv('SB_USER'),
        'PASSWORD': os.getenv('SB_PASSWORD'),
        'HOST': os.getenv('SB_HOST'),
        'PORT': os.getenv('SB_PORT'),
        'OPTIONS': {'sslmode': 'require'}
    }
}

AUTH_USER_MODEL = 'user.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATICFILES_DIRS = [BASE_DIR / 'global' / 'static']
STATIC_URL = 'static/'
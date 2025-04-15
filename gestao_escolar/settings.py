from pathlib import Path
import os
import dj_database_url

# Cloudinary
import cloudinary
import cloudinary_storage
import cloudinary
import cloudinary.uploader
import cloudinary.api

BASE_DIR = Path(__file__).resolve().parent.parent

# Segurança
SECRET_KEY = 'chave-insegura-para-dev'
DEBUG = True
ALLOWED_HOSTS = ['*']

# Aplicações
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'alunos',
    'funcionarios',
    'cloudinary',
    'cloudinary_storage',
    'controle',
]

# Middlewares
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gestao_escolar.urls'

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

WSGI_APPLICATION = 'gestao_escolar.wsgi.application'

# Banco de Dados (ajuste conforme seu banco real)
DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://neondb_owner:npg_BNlRh4PT1oxM@ep-misty-waterfall-a5v8jcb4-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require',
        conn_max_age=600,
        ssl_require=True
    )
}


# Validação de senha
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internacionalização
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Arquivos estáticos
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Cloudinary direto
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

import cloudinary
cloudinary.config(secure=True, debug=True)


CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dcwnkxjhd',
    'API_KEY': '938618262161565',
    'API_SECRET': 'a9lhiXNtZIENfXcnj8HP02r6n1k',
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

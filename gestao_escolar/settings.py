from pathlib import Path
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-str=d@-**sv13#x&ztx@h^y#mvj_g&(^&m(e)q!$*hbj)g!dr%'

DEBUG = True
ALLOWED_HOSTS = ['*']  # Ajuste com seu domínio do Render na produção

LOGIN_URL = '/login/'

INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',  # ✅ Para ajudar no dev com WhiteNoise
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'alunos',
    'funcionarios',
    'controle',
    'cloudinary',
    'cloudinary_storage',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ✅ WhiteNoise aqui
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

# ✅ Banco PostgreSQL (Neon)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'vitordias',
        'USER': 'root',
        'PASSWORD': 'Amv@1302',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Araguaina'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ✅ Arquivos Estáticos (Admin, CSS, JS)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# ✅ Render / Produção: garante que admin funcione
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ✅ Cloudinary para arquivos de mídia
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME', 'djxezavtr'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY', '475138434129133'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET', 'T9Cymt-w0xPSvbaygHqjk_d7DwE'),
}
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

cloudinary.config( 
    cloud_name = CLOUDINARY_STORAGE['CLOUD_NAME'], 
    api_key = CLOUDINARY_STORAGE['API_KEY'], 
    api_secret = CLOUDINARY_STORAGE['API_SECRET'],
    secure = True
)


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MESES_PT_BR = [
    "",  # índice 0 para alinhar com os meses de 1 a 12
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

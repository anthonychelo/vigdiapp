"""
ViGDi – settings.py (Version corrigée pour Cloudinary)
"""
from pathlib import Path
from decouple import config, Csv
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# ─── Sécurité ────────────────────────────────────────────────────────────────
SECRET_KEY    = config('SECRET_KEY', default='django-insecure-change-me-in-production')
DEBUG         = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='vigdiapp.onrender.com', cast=Csv())

# ─── Applications ─────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'cloudinary_storage',
    'cloudinary',
    'accounts',
    'marketplace',
    'messaging',
    'badges',
]

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

ROOT_URLCONF = 'videgrenier_cm.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'accounts.context_processors.user_badge',
            ],
        },
    },
]

WSGI_APPLICATION = 'videgrenier_cm.wsgi.application'

# ─── Base de données ──────────────────────────────────────────────────────────
DATABASE_URL = config('DATABASE_URL', default='')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ─── Authentification ─────────────────────────────────────────────────────────
AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_URL           = '/auth/login/'
LOGIN_REDIRECT_URL  = '/marketplace/'
LOGOUT_REDIRECT_URL = '/auth/login/'

# ─── Internationalisation ─────────────────────────────────────────────────────
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE     = 'Africa/Douala'
USE_I18N = True
USE_TZ   = True

# ─── Fichiers statiques ───────────────────────────────────────────────────────
STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ─── Stockage des médias (CONFIGURATION CORRIGÉE) ─────────────────────────────
MEDIA_STORAGE = config('MEDIA_STORAGE', default='local')

if MEDIA_STORAGE == 'cloudinary':
    # IMPORTANT : Configuration Cloudinary AVANT DEFAULT_FILE_STORAGE
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
    
    cloudinary.config(
        cloud_name = config('CLOUDINARY_CLOUD_NAME'),
        api_key = config('CLOUDINARY_API_KEY'),
        api_secret = config('CLOUDINARY_API_SECRET'),
        secure = True
    )
    
    # Utiliser le storage Cloudinary
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    
    # Configuration du storage
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME'),
        'API_KEY': config('CLOUDINARY_API_KEY'),
        'API_SECRET': config('CLOUDINARY_API_SECRET'),
    }
    
    # MEDIA_URL doit être vide ou '/' pour que cloudinary_storage génère les bonnes URLs
    MEDIA_URL = '/media/'
else:
    # Configuration locale (développement)
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# ─── Crispy Forms ─────────────────────────────────────────────────────────────
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK          = 'bootstrap5'

# ─── Limites upload ───────────────────────────────────────────────────────────
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── Email ────────────────────────────────────────────────────────────────────
EMAIL_BACKEND       = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST          = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT          = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS       = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER     = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL  = 'ViGDi <noreply@vigdi.cm>'

# ─── Sécurité HTTPS (production) ─────────────────────────────────────────────
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT     = True
    SESSION_COOKIE_SECURE   = True
    CSRF_COOKIE_SECURE      = True
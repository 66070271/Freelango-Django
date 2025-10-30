from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
STATICFILES_DIRS = [
    os.path.join(BASE_DIR.parent, "static"),  # ⬅️ ตรงนี้คือโฟลเดอร์ static ที่อยู่นอกโปรเจกต์
]
# --- Media / Static ---
# MEDIA_ROOT ไม่ต้องใช้แล้วเมื่อเก็บบน S3
MEDIA_URL = '/media/'

SECRET_KEY = 'django-insecure-vbd+u*fglzff8sr1&*t&k#y6kjtbfnj@ncw--5cqpmkrfgoi0%'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'service',
    'storages',   # ต้องมีอันนี้เพื่อให้ Django ใช้ S3 backend ได้
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

ROOT_URLCONF = 'freelance.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'freelance.wsgi.application'

# --- Database (RDS) ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "mydb",
        "USER": "postgres",
        "PASSWORD": "MyDbPass123!",
        "HOST": "project-db.cnrqorc6ypjd.us-east-1.rds.amazonaws.com",
        "PORT": "5432",
    }
}

# --- Language / Timezone ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Bangkok'
USE_I18N = True
USE_TZ = True

# === AWS S3 CONFIG ===
AWS_STORAGE_BUCKET_NAME = 'mart-django-bucket'   # ✅ ใช้ชื่อ bucket จริง
AWS_S3_REGION_NAME = 'ap-southeast-1'            # ✅ ตรวจ region ใน S3 console ด้วย
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = False
AWS_S3_SIGNATURE_VERSION = 's3v4'

# --- Static files ---
STATIC_LOCATION = 'static'
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/'
STATICFILES_STORAGE = 'freelance.storages_backends.StaticStorage'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# --- Media files ---
MEDIA_LOCATION = 'media'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIA_LOCATION}/'
DEFAULT_FILE_STORAGE = 'freelance.storages_backends.MediaStorage'

LOGIN_URL = '/login'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

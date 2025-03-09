from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
#BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-o9p7!!(y$7d1a5j@2d)u^cw$gq&bc5z_d9^es9ob_q8$&o8-x#'

# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = False
DEBUG=True
ALLOWED_HOSTS = ['*']


# Application definition
INSTALLED_APPS = [
    'inventory.apps.InventoryConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'tailwind',
    'theme',
    'fontawesomefree',
    'django_filters',
    'django_fastdev',
    'import_export',
    'simple_history',
    # 'redisboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "django.middleware.cache.UpdateCacheMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    "django.middleware.common.CommonMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.redis.RedisCache",
#         "LOCATION": "redis://127.0.0.1:6379",
#     }
# }


# # # Cache settings
# CACHE_MIDDLEWARE_SECONDS = 60 * 60
# CACHE_MIDDLEWARE_KEY_PREFIX = "store"
# CACHE_MIDDLEWARE_ALIAS = "default"

ROOT_URLCONF = 'store.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'store.wsgi.application'

TAILWIND_APP_NAME='theme'
INTERNAL_IPS=['127.0.0.1']
NPM_BIN_PATH = "/usr/bin/npm"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE':'django.db.backends.postgresql',
#         # 'NAME':'store_nohd',
#         'NAME':'nohd_store',
#     	# 'USER':'sadmin',
# 	    # 'PASSWORD':'s2024db',
#     	'USER':'postgres',
# 	    'PASSWORD':'8080mali',
# 	    'HOST':'localhost',
# 	    'PORT':'5432',
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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

TIME_ZONE = 'Africa/Lagos'

USE_I18N = False

USE_L10N=True

USE_THOUSAND_SEPARATOR=True

USE_TZ = True

DATE_INPUT_FORMATS = ['%d-%m-%Y']
DATETIME_INPUT_FORMAT=['%d-%m-%Y']

LOGIN_REDIRECT_URL = '/'
LOGIN_URL="/login/"


STATIC_URL = '/static/'
STATIC_ROOT=os.path.join(BASE_DIR,'static')


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR,'media/')

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

SESSION_COOKIE_AGE = 3600  
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Log out when browser closes
SESSION_SAVE_EVERY_REQUEST = True  # Reset session timeout on activity
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#TESTING = True

SESSION_COOKIE_AGE = 3600
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_SECURE = False

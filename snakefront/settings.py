"""
Django settings for snakefront project.

Generated by 'django-admin startproject' using Django 3.2.16.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os
import tempfile
import sys
import yaml
from django.core.management.utils import get_random_secret_key
from users.utils import get_username
from datetime import datetime
from importlib import import_module

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-q*aurr9x9v_$%#pt53^t*0c@d%hi190ka9r6-=9(=mxbqtknof'

SETTINGS_FILE = os.path.join(BASE_DIR, "snakefront/settings.yml")
if not os.path.exists(SETTINGS_FILE):
    sys.exit("Global settings file settings.yml is missing in the install directory.")


# Read in the settings file to get settings
class Settings:
    """convert a dictionary of settings (from yaml) into a class"""

    def __init__(self, dictionary):
        for key, value in dictionary.items():
            setattr(self, key, value)
        setattr(self, "UPDATED_AT", datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))

    def __str__(self):
        return "[snakefront-settings]"

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        for key, value in self.__dict__.items():
            yield key, value


with open(SETTINGS_FILE, "r") as fd:
    cfg = Settings(yaml.load(fd.read(), Loader=yaml.FullLoader))

# For each setting, if it's defined in the environment with SNAKEFRONT_ prefix, override
for key, value in cfg:
    envar = os.getenv("SNAKEFRONT_%s" % key)
    if envar:
        setattr(cfg, key, envar)

def generate_secret_key(filename):
    """A helper function to write a randomly generated secret key to file"""
    key = get_random_secret_key()
    with open(filename, "w") as fd:
        fd.writelines("SECRET_KEY = '%s'" % key)


# Generate secret key if doesn't exist, and not defined in environment
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    try:
        from .secret_key import SECRET_KEY
    except ImportError:
        SETTINGS_DIR = os.path.abspath(os.path.dirname(__file__))
        generate_secret_key(os.path.join(SETTINGS_DIR, "secret_key.py"))
        from .secret_key import SECRET_KEY

# Private only should be a boolean
cfg.PRIVATE_ONLY = cfg.PRIVATE_ONLY is not None

# Set the domain name
DOMAIN_NAME = cfg.DOMAIN_NAME
if cfg.DOMAIN_PORT:
    DOMAIN_NAME = "%s:%s" % (DOMAIN_NAME, cfg.DOMAIN_PORT)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if os.getenv("DEBUG") != "false" else False

# Derive list of plugins enabled from the environment
PLUGINS_LOOKUP = {
    "ldap_auth": False,
    "pam_auth": False,
    "saml_auth": False,
}
PLUGINS_ENABLED = []
using_auth_backend = False
for key, enabled in PLUGINS_LOOKUP.items():
    plugin_key = "PLUGIN_%s_ENABLED" % key.upper()
    if hasattr(cfg, plugin_key) and getattr(cfg, plugin_key) is not None:

        # Don't enable auth backends if we are using a notebook
        if cfg.NOTEBOOK_ONLY or cfg.NOTEBOOK and "AUTH" in plugin_key:
            continue

        if "AUTH" in plugin_key:
            using_auth_backend = True
        PLUGINS_ENABLED.append(key)

# Does the user want a notebook? Default to this if no auth setup
if not hasattr(cfg, "NOTEBOOK"):
    cfg.NOTEBOOK = True if not using_auth_backend else None

# If the working directory isn't defined, set to pwd
if not hasattr(cfg, "WORKDIR") or not cfg.WORKDIR:
    cfg.WORKDIR = os.getcwd()


ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.humanize',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'crispy_forms',
    # 'social_django',
    'django_q',
    'rest_framework',
    'rest_framework.authtoken',
    # 'users',
    'api',
    'base',
    'main',
    'accounts',
    'project',
    'scheduler',
    'django_celery_beat',
    'django_celery_results',
    's3browser',
]

CRISPY_TEMPLATE_PACK = "bootstrap4"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


if cfg.ENABLE_CACHE:
    MIDDLEWARE += [
        "django.middleware.cache.UpdateCacheMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.cache.FetchFromCacheMiddleware",
    ]

    CACHE_MIDDLEWARE_ALIAS = "default"
    CACHE_MIDDLEWARE_SECONDS = 86400  # one day


# If we are using a notebook, use an in memory channel layer
# if cfg.NOTEBOOK:
#     CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}


ROOT_URLCONF = 'snakefront.urls'

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
                'snakefront.context_processors.globals',
            ],
        },
    },
]

TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG
WSGI_APPLICATION = 'snakefront.wsgi.application'
ASGI_APPLICATION = 'snakefront.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

# AUTH_USER_MODEL = "users.User"
# SOCIAL_AUTH_USER_MODEL = "users.User"
GRAVATAR_DEFAULT_IMAGE = "retro"

AUTH_USER_MODEL = "accounts.CustomUser"
AUTHENTICATION_BACKENDS = ['accounts.backends.EmailBackend']

# Cache to tmp
CACHE_LOCATION = os.path.join(tempfile.gettempdir(), "snakefront-cache")
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": CACHE_LOCATION,
    }
}
if not os.path.exists(CACHE_LOCATION):
    os.mkdir(CACHE_LOCATION)
# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "USER": 'snake',
            "PASSWORD": 'snake1234',
            "NAME": 'snakefront',
            "HOST": '127.0.0.1',  # Set to IP address
            "PORT": "",  # empty string for default.
        }
    }

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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

Q_CLUSTER = {
    "name": "snakecluster",
    "timeout": 90,
    "retry": 120,
    "queue_limit": 50,
    "bulk": 10,
    "orm": "default",
}

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_ROOT = "static"
STATIC_URL = "/static/"
MEDIA_ROOT = "data"
MEDIA_URL = "/data/"


VIEW_RATE_LIMIT = "1000/1d"  # The rate limit for each view, django-ratelimit, "50 per day per ipaddress)
VIEW_RATE_LIMIT_BLOCK = (
    True  # Given that someone goes over, are they blocked for the period?
)

LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "/login"

cfg.USERNAME = None
if cfg.NOTEBOOK or cfg.NOTEBOOK_ONLY:
    cfg.USERNAME = get_username()


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]

# Apply any plugin settings
for plugin in PLUGINS_ENABLED:

    plugin_module = "snakefront.plugins." + plugin
    plugin = import_module(plugin_module)

    # Add the plugin to INSTALLED APPS
    INSTALLED_APPS.append(plugin_module)

    # Add AUTHENTICATION_BACKENDS if defined, for authentication plugins
    if hasattr(plugin, "AUTHENTICATION_BACKENDS"):
        AUTHENTICATION_BACKENDS = (
            AUTHENTICATION_BACKENDS + plugin.AUTHENTICATION_BACKENDS
        )

    # Add custom context processors, if defines for plugin
    if hasattr(plugin, "CONTEXT_PROCESSORS"):
        for context_processor in plugin.CONTEXT_PROCESSORS:
            TEMPLATES[0]["OPTIONS"]["context_processors"].append(context_processor)


CELERY_BROKER_URL = 'redis://127.0.0.1:6379'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TAST_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Seoul'

#AWS SETTING
AWS_ACCESS_KEY_ID = "****************"
AWS_SECRET_ACCESS_KEY = "*****************"
AWS_STORAGE_BUCKET_NAME = "sample-bucket"
AWS_AUTO_CREATE_BUCKET = True
AWS_QUERYSTRING_AUTH = False
AWS_EXPIRY = 60 * 60 * 24 * 7
control = 'max-age=%d, s-maxage=%d, must-revalidate' % (AWS_EXPIRY, AWS_EXPIRY)
AWS_HEADERS = {
    'Cache-Control': bytes(control, encoding='latin-1')
}
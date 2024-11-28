"""
Django settings for server project.

Generated by 'django-admin startproject' using Django 4.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os

from ..const import CONFIG, PROJECT_DIR

BASE_DIR = PROJECT_DIR
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = CONFIG.SECRET_KEY

DEBUG = CONFIG.DEBUG
# SECURITY WARNING: If you run with debug turned on, more debug msg with be log
DEBUG_DEV = CONFIG.DEBUG_DEV

LOG_LEVEL = CONFIG.LOG_LEVEL

# 如果前端是代理，则可以通过该配置，在系统构建url的时候，获取正确的 scheme
# 需要在 前端加入该配置  proxy_set_header X-Forwarded-Proto $scheme;
# https://docs.djangoproject.com/zh-hans/4.2/ref/settings/#std-setting-SECURE_PROXY_SSL_HEADER
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# 为了兼容前端NGINX代理，并且使用非80，443端口访问，详细查看源码：django.http.request.HttpRequest._get_raw_host
# https://docs.djangoproject.com/zh-hans/4.2/ref/settings/#use-x-forwarded-host
USE_X_FORWARDED_HOST = True

ALLOWED_HOSTS = ["*"]

# Application definition
XADMIN_APPS = CONFIG.XADMIN_APPS

# 表前缀设置
# 1.指定配置
# DB_PREFIX={
# 'system': 'abc_', # system app所有的表都加前缀 abc_
# 'system.config':'xxa_', # 仅system.config添加前缀 xxa_
# '': '', # 默认前缀
# }
#
# 2.全局配置
# DB_PREFIX='abc_'  : 所有表都添加 abc_
DB_PREFIX = CONFIG.DB_PREFIX

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'system.apps.SystemConfig',  # 系统管理
    'settings.apps.SettingsConfig',  # 设置相关
    "notifications.apps.NotificationsConfig",  # 消息通知相关
    'captcha.apps.CaptchaConfig',  # 图片验证码
    'message.apps.MessageConfig',  # websocket 消息
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'rest_framework',
    'django_filters',
    'django_celery_results',
    'django_celery_beat',
    'imagekit',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    *XADMIN_APPS,
    'common.apps.CommonConfig',  # 这个放到最后, django ready
]

if DEBUG or DEBUG_DEV:
    INSTALLED_APPS.insert(0, 'daphne')  # 支持websocket

MIDDLEWARE = [
    'server.middleware.StartMiddleware',
    'server.middleware.RequestMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'server.middleware.RefererCheckMiddleware',
    'server.middleware.SQLCountMiddleware',
    'common.core.middleware.ApiLoggingMiddleware',
    'server.middleware.EndMiddleware'
]

ROOT_URLCONF = 'server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_DIR, 'templates')]
        ,
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

# WSGI_APPLICATION = 'server.wsgi.application'
ASGI_APPLICATION = "server.asgi.application"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# Redis 配置
REDIS_HOST = CONFIG.REDIS_HOST
REDIS_PORT = CONFIG.REDIS_PORT
REDIS_PASSWORD = CONFIG.REDIS_PASSWORD

DEFAULT_CACHE_ID = CONFIG.DEFAULT_CACHE_ID
CHANNEL_LAYERS_CACHE_ID = CONFIG.CHANNEL_LAYERS_CACHE_ID
CELERY_BROKER_CACHE_ID = CONFIG.CELERY_BROKER_CACHE_ID
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{DEFAULT_CACHE_ID}",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 8000},
            "PASSWORD": REDIS_PASSWORD,
            "DECODE_RESPONSES": True,
            "REDIS_CLIENT_KWARGS": {"health_check_interval": 30},
        },
        "TIMEOUT": 60 * 15,
        "KEY_FUNCTION": "common.base.utils.redis_key_func",
        "REVERSE_KEY_FUNCTION": "common.base.utils.redis_reverse_key_func",
    },
}

# create database xadmin default character set utf8 COLLATE utf8_general_ci;
# grant all on xadmin.* to server@'127.0.0.1' identified by 'KGzKjZpWBp4R4RSa';
# python manage.py makemigrations
# python manage.py migrate

DB_OPTIONS = {}
DB_ENGINE = CONFIG.DB_ENGINE.lower()
if DB_ENGINE in ['mysql', 'oracle', 'postgresql', 'sqlite3']:
    ENGINE = 'django.db.backends.{}'.format(DB_ENGINE)
else:
    ENGINE = CONFIG.DB_ENGINE

DATABASES = {
    'default': {
        'ENGINE': DB_ENGINE,
        'NAME': CONFIG.DB_DATABASE,
        'HOST': CONFIG.DB_HOST,
        'PORT': CONFIG.DB_PORT,
        'USER': CONFIG.DB_USER,
        'PASSWORD': CONFIG.DB_PASSWORD,
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 600,
        'OPTIONS': DB_OPTIONS
    }
}

if DB_ENGINE == 'mysql':
    DB_OPTIONS['init_command'] = "SET sql_mode='STRICT_TRANS_TABLES'"
    DB_OPTIONS['charset'] = "utf8mb4"
    DB_OPTIONS['collation'] = "utf8mb4_bin"

# https://docs.djangoproject.com/zh-hans/5.0/topics/db/multi-db/#automatic-database-routing
# 读写分离 可能会出现 the current database router prevents this relation.
# 1.项目设置了router读写分离，且在ORM create()方法中，使用了前边filter()方法得到的数据，
# 2.由于django是惰性查询，前边的filter()并没有立即查询，而是在create()中引用了filter()的数据时，执行了filter()，
# 3.此时写操作的db指针指向write_db，filter()的db指针指向read_db，两者发生冲突，导致服务禁止了此次与mysql的交互
# 解决办法：
# 在前边filter()方法中，使用using()方法，使filter()方法立即与数据库交互，查出数据。
# Author.objects.using("default")
# >>> p = Person(name="Fred")
# >>> p.save(using="second")  # (statement 2)

DATABASE_ROUTERS = ['common.core.db.router.DBRouter']

# websocket 消息需要用到redis的消息发布订阅
CHANNEL_LAYERS = {
    "default": {
        # "BACKEND": "channels_redis.core.RedisChannelLayer",
        "BACKEND": "channels_redis.pubsub.RedisPubSubChannelLayer",
        "CONFIG": {
            "hosts": [f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{CHANNEL_LAYERS_CACHE_ID}"],
        },
    },
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
# http://www.i18nguy.com/unicode/language-identifiers.html
# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = CONFIG.LANGUAGE_CODE

TIME_ZONE = CONFIG.TIME_ZONE

USE_I18N = True

USE_TZ = True

AUTH_USER_MODEL = "system.UserInfo"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'api/static/'
STATIC_ROOT = os.path.join(PROJECT_DIR, "data", "static")

# STATICFILES_FINDERS = (
#     "django.contrib.staticfiles.finders.FileSystemFinder",
#     "django.contrib.staticfiles.finders.AppDirectoriesFinder"
# )
# 收集静态文件
# python manage.py collectstatic


# Media配置
MEDIA_URL = "media/"
MEDIA_ROOT = os.path.join(PROJECT_DIR, "data", "upload")
FILE_UPLOAD_SIZE = CONFIG.FILE_UPLOAD_SIZE
PICTURE_UPLOAD_SIZE = CONFIG.PICTURE_UPLOAD_SIZE
FILE_UPLOAD_HANDLERS = [
    "django.core.files.uploadhandler.MemoryFileUploadHandler",
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# I18N translation
LOCALE_PATHS = [
    os.path.join(PROJECT_DIR, 'locale'),
]

CACHE_KEY_TEMPLATE = {
    'config_key': 'config',
    'make_token_key': 'make_token',
    'download_url_key': 'download_url',
    'pending_state_key': 'pending_state',
    'user_websocket_key': 'user_websocket',
    'upload_part_info_key': 'upload_part_info',
    'black_access_token_key': 'black_access_token',
    'common_resource_ids_key': 'common_resource_ids'
}

APPEND_SLASH = False

HTTP_BIND_HOST = CONFIG.HTTP_BIND_HOST
HTTP_LISTEN_PORT = CONFIG.HTTP_LISTEN_PORT
GUNICORN_MAX_WORKER = CONFIG.GUNICORN_MAX_WORKER
# celery flower 任务监控配置
CELERY_FLOWER_PORT = CONFIG.CELERY_FLOWER_PORT
CELERY_FLOWER_HOST = CONFIG.CELERY_FLOWER_HOST
CELERY_FLOWER_AUTH = CONFIG.CELERY_FLOWER_AUTH

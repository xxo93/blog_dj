"""
Django settings for blog_dj project.

Generated by 'django-admin startproject' using Django 3.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import sys
import datetime

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 新增一个系统导包路径
sys.path.insert(0, os.path.join(BASE_DIR, "apps"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$947f)rz-*tx@4wca8*k$o+($mh47=i-v$ufvguv=1@ou8x#^p'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    '192.168.137.1',
    'localhost',
    '127.0.0.1',
]

# CORS组的配置信息---添加白名单
CORS_ORIGIN_WHITELIST = (
    # 'http://www.DomainName.com:8088',
)
CORS_ALLOW_CREDENTIALS = True   # 允许ajax跨域请求时携带cookie
CORS_ORIGIN_ALLOW_ALL = True    # 所有的访问都将被允许，白名单不会被使用，默认为false

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',  # 添加cors跨域组件
    'rest_framework',   # 添加drf
    # 'django_filters',

    # 子应用
    'blog_dj.apps.apptest',     # 测试
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',    # 解决跨域问题的中间件
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'blog_dj.urls'

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

WSGI_APPLICATION = 'blog_dj.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 数据库引擎
        'NAME': 'user_db',  # 数据库名
        'USER': 'root',  # 账户名
        'PASSWORD': 'root',  # 密码
        'HOST': '127.0.0.1',  # 主机
        'PORT': '3306',  # 端口
    },
    'bom_db': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bom_db',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    },
}

# todo set database Maping 配置多数据库
DATABASE_ROUTERS = ['blog_dj.database_router.DatabaseAppsRouter']
DATABASE_APPS_MAPPING = {
    # example:
    # 'app_name':'database_name',
    'apptest': 'bom_db',
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'zh-hans'
# TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

# django-redis配置
# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/3",
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#             # 'PASSWORD': '', 密码配置
#         }
#     },
#     'local_cache': {
#         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#         'LOCATION': 'unique-snowflake',
#         "OPTIONS": {
#             "MAX_ENTERS": 100
#         }
#     }
# }

# rest_framework相关配置
# REST_FRAMEWORK = {
#     # 身份校验
#     'DEFAULT_AUTHENTICATION_CLASSES': (
#         #     'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
#         #     'rest_framework.authentication.SessionAuthentication',
#         #     'rest_framework.authentication.BasicAuthentication',
#
#         # 'blog_dj.utils.UserAuthentication.UserAuth',
#     ),
#
#     # 权限管理
#     "DEFAULT_PERMISSION_CLASSES": (
#         # 'blog_dj.utils.permissions.ModulePermission',
#         # 'blog_dj.utils.permissions.UrlPermission',
#     ),
#
#     # 过滤配置  根据条件来查找数据
#     'DEFAULT_FILTER_BACKENDS': (
#         'django_filters.rest_framework.DjangoFilterBackend',
#     ),
#
#     # 分页配置
#     # 扩展默认分页类，支持参数设置分页大小，默认分页大小参数：page_size
#     'DEFAULT_PAGINATION_CLASS': 'blog_dj.utils.GlobalPagination.PageNumberSizePagination',
#     'PAGE_SIZE': 10,  # 每页几条数据
# }

# jwt 配置
# JWT_AUTH = {
#     'JWT_EXPIRATION_DELTA': datetime.timedelta(hours=24),  # 过期时间
# }

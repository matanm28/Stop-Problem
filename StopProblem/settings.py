"""
Django settings for StopProblem project.

Generated by 'django-admin startproject' using Django 3.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path

from configurations import Configuration


class Base(Configuration):
    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = 'django-insecure-7=qqlq%as8iv(46kkos4(#!_u7_yt0t3pv=emv!@i0iv@pe#!j'

    # Application definition

    INSTALLED_APPS = [
        'stop_problem',
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'crispy_forms',
        'rest_framework',
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
    ROOT_URLCONF = 'StopProblem.urls'

    @property
    def TEMPLATES(self):
        return [
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': [os.path.join(self.BASE_DIR, 'templates')]
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

    WSGI_APPLICATION = 'StopProblem.wsgi.application'

    # Database
    # https://docs.djangoproject.com/en/3.2/ref/settings/#databases

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'dfnnu10q8dgl74',
            'HOST': 'ec2-54-216-17-9.eu-west-1.compute.amazonaws.com',
            'PORT': 5432,
            'USER': 'klhvlmifthowwk',
            'PASSWORD': '3b84b81a1cc72cee1b156d46cf8d46c76bcd701ca6978c6dccec3149d3504527',
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

    # Internationalization
    # https://docs.djangoproject.com/en/3.2/topics/i18n/

    LANGUAGE_CODE = 'en-us'

    TIME_ZONE = 'UTC'

    USE_I18N = True

    USE_L10N = True

    USE_TZ = True

    STATIC_URL = '/static/'

    # Extra places for collectstatic to find static files.
    @property
    def STATICFILES_DIRS(self):
        return [os.path.join(self.BASE_DIR, 'static'), ]

    # Default primary key field type
    # https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

    DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


class Develop(Base):
    # Build paths inside the project like this: BASE_DIR / 'subdir'.
    BASE_DIR = Path(__file__).resolve().parent.parent
    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = True
    ALLOWED_HOSTS = ['127.0.0.1']


class Production(Base):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = False
    ALLOWED_HOSTS = ['https://stop-problem.herokuapp.com/',
                     'http://stop-problem.herokuapp.com/',
                     'stop-problem.herokuapp.com/',
                     'stop-problem.herokuapp.com']
    MIDDLEWARE = ['whitenoise.middleware.WhiteNoiseMiddleware', *Base.MIDDLEWARE]

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/3.2/howto/static-files/

    PROJECT_ROOT = os.path.join(os.path.abspath(__file__))
    STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
    # Extra lookup directories for collectstatic to find static files
    STATICFILES_DIRS = (
        os.path.join(PROJECT_ROOT, 'static'),
    )

    #  Add configuration for static files storage using whitenoise
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

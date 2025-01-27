import os

from django.urls import reverse_lazy
import dj_database_url
import environ
from elasticsearch import RequestsHttpConnection
from elasticsearch_dsl.connections import connections

import healthcheck.backends
import directory_healthcheck.backends


env = environ.Env()
env.read_env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', False)

# As app is running behind a host-based router supplied by Heroku or other
# PaaS, we can open ALLOWED_HOSTS
ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'rest_framework',
    'django_extensions',
    'django_celery_beat',
    'raven.contrib.django.raven_compat',
    'usermanagement',
    'field_history',
    'core.apps.CoreConfig',
    'enrolment.apps.EnrolmentConfig',
    'company.apps.CompanyConfig',
    'user.apps.UserConfig',
    'supplier.apps.SupplierConfig',
    'buyer.apps.BuyerConfig',
    'contact.apps.ContactConfig',
    'notifications.apps.NotificationsConfig',
    'activitystream.apps.ActivityStreamConfig',
    'exporting.apps.ExportingConfig',
    'directory_constants',
    'directory_healthcheck',
    'health_check.db',
    'health_check.cache',
    'testapi',
    'authbroker_client',
]

MIDDLEWARE_CLASSES = [
    'core.middleware.SignatureCheckMiddleware',
    'core.middleware.AdminPermissionCheckMiddleware',
    'admin_ip_restrictor.middleware.AdminIPRestrictorMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
]

ROOT_URLCONF = 'conf.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_ROOT, 'templates')],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                'django.template.loaders.eggs.Loader',
            ],
        },
    },
]

WSGI_APPLICATION = 'conf.wsgi.application'


VCAP_SERVICES = env.json('VCAP_SERVICES', {})
VCAP_APPLICATION = env.json('VCAP_APPLICATION', {})

if 'redis' in VCAP_SERVICES:
    REDIS_CACHE_URL = VCAP_SERVICES['redis'][0]['credentials']['uri']
    REDIS_CELERY_URL = REDIS_CACHE_URL.replace('rediss://', 'redis://')
else:
    REDIS_CACHE_URL = env.str('REDIS_CACHE_URL', '')
    REDIS_CELERY_URL = env.str('REDIS_CELERY_URL', '')

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DATABASES = {
    'default': dj_database_url.config()
}

# Caches
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        # separate to REDIS_CELERY_URL as needs to start with 'rediss' for SSL
        'LOCATION': REDIS_CACHE_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'


# Static files served with Whitenoise and AWS Cloudfront
# http://whitenoise.evans.io/en/stable/django.html#instructions-for-amazon-cloudfront
# http://whitenoise.evans.io/en/stable/django.html#restricting-cloudfront-to-static-files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
if not os.path.exists(STATIC_ROOT):
    os.makedirs(STATIC_ROOT)
STATIC_HOST = env.str('STATIC_HOST', '')
STATIC_URL = STATIC_HOST + '/api-static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# S3 storage does not use these settings, needed only for dev local storage
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# parity with nginx config for maximum request body
DATA_UPLOAD_MAX_MEMORY_SIZE = 6 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 6 * 1024 * 1024

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

for static_dir in STATICFILES_DIRS:
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

# SSO config
FEATURE_ENFORCE_STAFF_SSO_ENABLED = env.bool('FEATURE_ENFORCE_STAFF_SSO_ENABLED', False)
if FEATURE_ENFORCE_STAFF_SSO_ENABLED:
    AUTHENTICATION_BACKENDS = [
        'django.contrib.auth.backends.ModelBackend',
        'authbroker_client.backends.AuthbrokerBackend'
    ]

    LOGIN_URL = reverse_lazy('authbroker_client:login')
    LOGIN_REDIRECT_URL = reverse_lazy('admin:index')

    # authbroker config
AUTHBROKER_URL = env.str('STAFF_SSO_AUTHBROKER_URL')
AUTHBROKER_CLIENT_ID = env.str('AUTHBROKER_CLIENT_ID')
AUTHBROKER_CLIENT_SECRET = env.str('AUTHBROKER_CLIENT_SECRET')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('SECRET_KEY')

# DRF
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'core.authentication.SessionAuthenticationSSO',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'core.permissions.IsAuthenticatedSSO',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}


# Sentry
RAVEN_CONFIG = {
    'dsn': env.str('SENTRY_DSN', ''),
}

# Logging for development
if DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django.request': {
                'handlers': ['console'],
                'level': 'ERROR',
                'propagate': True,
            },
            'mohawk': {
                'handlers': ['console'],
                'level': 'WARNING',
                'propagate': False,
            },
            'requests': {
                'handlers': ['console'],
                'level': 'WARNING',
                'propagate': False,
            },
            'elasticsearch': {
                'handlers': ['console'],
                'level': 'WARNING',
                'propagate': False,
            },
            '': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': False,
            },
        }
    }
else:
    # Sentry logging
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'root': {
            'level': 'WARNING',
            'handlers': ['sentry'],
        },
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s '
                          '%(process)d %(thread)d %(message)s'
            },
        },
        'handlers': {
            'sentry': {
                'level': 'ERROR',
                'class': (
                    'raven.contrib.django.raven_compat.handlers.SentryHandler'
                ),
                'tags': {'custom-tag': 'x'},
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            }
        },
        'loggers': {
            'django.db.backends': {
                'level': 'ERROR',
                'handlers': ['console'],
                'propagate': False,
            },
            'raven': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
            'sentry.errors': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
        },
    }

# CH
COMPANIES_HOUSE_API_KEY = env.str('COMPANIES_HOUSE_API_KEY', '')

# Settings for company email confirmation
COMPANY_EMAIL_CONFIRMATION_SUBJECT = env.str(
    'COMPANY_EMAIL_CONFIRMATION_SUBJECT',
)
COMPANY_EMAIL_CONFIRMATION_FROM = env.str(
    'COMPANY_EMAIL_CONFIRMATION_FROM'
)
COMPANY_EMAIL_CONFIRMATION_URL = env.str(
    'COMPANY_EMAIL_CONFIRMATION_URL'
)

# Email
EMAIL_BACKED_CLASSES = {
    'default': 'django.core.mail.backends.smtp.EmailBackend',
    'console': 'django.core.mail.backends.console.EmailBackend'
}
EMAIL_BACKED_CLASS_NAME = env.str('EMAIL_BACKEND_CLASS_NAME', 'default')
EMAIL_BACKEND = EMAIL_BACKED_CLASSES[EMAIL_BACKED_CLASS_NAME]
EMAIL_HOST = env.str('EMAIL_HOST', '')
EMAIL_PORT = env.str('EMAIL_PORT', '')
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = env.str('DEFAULT_FROM_EMAIL', '')
FAS_FROM_EMAIL = env.str('FAS_FROM_EMAIL', '')
FAB_FROM_EMAIL = env.str('FAB_FROM_EMAIL', '')
FAB_OWNERSHIP_URL = env.str('FAB_OWNERSHIP_URL', '')
FAB_COLLABORATOR_URL = env.str('FAB_COLLABORATOR_URL', '')
OWNERSHIP_INVITE_SUBJECT = env.str(
    'OWNERSHIP_INVITE_SUBJECT',
    'Confirm ownership of {company_name}’s Find a buyer profile'
)
COLLABORATOR_INVITE_SUBJECT = env.str(
    'COLLABORATOR_INVITE_SUBJECT',
    'Confirm you’ve been added to {company_name}’s Find a buyer profile'
)

# Public storage for company profile logo
STORAGE_CLASSES = {
    'default': 'storages.backends.s3boto3.S3Boto3Storage',
    'local-storage': 'django.core.files.storage.FileSystemStorage',
}
STORAGE_CLASS_NAME = env.str('STORAGE_CLASS_NAME', 'default')
DEFAULT_FILE_STORAGE = STORAGE_CLASSES[STORAGE_CLASS_NAME]
LOCAL_STORAGE_DOMAIN = env.str('LOCAL_STORAGE_DOMAIN', '')
AWS_AUTO_CREATE_BUCKET = True
AWS_S3_FILE_OVERWRITE = False
AWS_S3_CUSTOM_DOMAIN = env.str('AWS_S3_CUSTOM_DOMAIN', '')
AWS_S3_URL_PROTOCOL = env.str('AWS_S3_URL_PROTOCOL', 'https:')
# Needed for new AWS regions
# https://github.com/jschneier/django-storages/issues/203
AWS_S3_SIGNATURE_VERSION = env.str('AWS_S3_SIGNATURE_VERSION', 's3v4')
AWS_QUERYSTRING_AUTH = env.bool('AWS_QUERYSTRING_AUTH', False)
S3_USE_SIGV4 = env.bool('S3_USE_SIGV4', True)
AWS_S3_HOST = env.str('AWS_S3_HOST', 's3.eu-west-1.amazonaws.com')

if 'aws-s3-bucket' in VCAP_SERVICES:
    AWS_S3_DEFAULT_BINDING_BUCKET_NAME = env.str('AWS_S3_DEFAULT_BINDING_BUCKET_NAME')
    AWS_S3_DATA_SCIENCE_BINDING_BUCKET_NAME = env.str('AWS_S3_DATASCIENCE_BINDING_BUCKET_NAME')

    bucket_credentials_map = {
        item['name']: item
        for item in VCAP_SERVICES['aws-s3-bucket']
    }

    default_credentials = bucket_credentials_map[AWS_S3_DEFAULT_BINDING_BUCKET_NAME]
    datascience_credentials = bucket_credentials_map[AWS_S3_DATA_SCIENCE_BINDING_BUCKET_NAME]

    # Setting up the the main S3 PaSS bucket
    credentials = default_credentials['credentials']
    AWS_ACCESS_KEY_ID = credentials['aws_access_key_id']
    AWS_SECRET_ACCESS_KEY = credentials['aws_secret_access_key']
    AWS_STORAGE_BUCKET_NAME = credentials['bucket_name']
    AWS_S3_REGION_NAME = credentials['aws_region']
    AWS_S3_ENCRYPTION = True
    AWS_DEFAULT_ACL = None

    # Setting up the the datascience s3 PaSS bucket
    credentials = datascience_credentials['credentials']
    AWS_ACCESS_KEY_ID_DATA_SCIENCE = credentials['aws_access_key_id']
    AWS_SECRET_ACCESS_KEY_DATA_SCIENCE = credentials['aws_secret_access_key']
    AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE = credentials['bucket_name']
    AWS_S3_REGION_NAME_DATA_SCIENCE = credentials['aws_region']
    AWS_S3_ENCRYPTION_DATA_SCIENCE = True
    AWS_DEFAULT_ACL_DATA_SCIENCE = None

# Admin proxy
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_DOMAIN = env.str('SESSION_COOKIE_DOMAIN', 'great.gov.uk')
SESSION_COOKIE_NAME = 'directory_api_admin_session_id'
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', True)
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', True)

# Verification letters sent with stannp.com

STANNP_API_KEY = env.str('STANNP_API_KEY', '')
STANNP_TEST_MODE = env.bool('STANNP_TEST_MODE', True)
STANNP_VERIFICATION_LETTER_TEMPLATE_ID = env.str(
    'STANNP_VERIFICATION_LETTER_TEMPLATE_ID'
)

# directory forms api client
DIRECTORY_FORMS_API_BASE_URL = env.str('DIRECTORY_FORMS_API_BASE_URL')
DIRECTORY_FORMS_API_API_KEY = env.str('DIRECTORY_FORMS_API_API_KEY')
DIRECTORY_FORMS_API_SENDER_ID = env.str('DIRECTORY_FORMS_API_SENDER_ID')
DIRECTORY_FORMS_API_DEFAULT_TIMEOUT = env.int('DIRECTORY_API_FORMS_DEFAULT_TIMEOUT', 5)
DIRECTORY_FORMS_API_ZENDESK_SEVICE_NAME = env.str('DIRECTORY_FORMS_API_ZENDESK_SEVICE_NAME', 'api')

# Verification letters sent with govnotify
GOVNOTIFY_VERIFICATION_LETTER_TEMPLATE_ID = env.str(
    'GOVNOTIFY_VERIFICATION_LETTER_TEMPLATE_ID',
    '22d1803a-8af5-4b06-bc6c-ffc6573c4c7d'
)

# Registration letters template id
GOVNOTIFY_REGISTRATION_LETTER_TEMPLATE_ID = env.str(
    'GOVNOTIFY_REGISTRATION_LETTER_TEMPLATE_ID',
    '8840eba9-5c5b-4f87-b495-6127b7d3e2c9'
)

GECKO_API_KEY = env.str('GECKO_API_KEY', '')
# At present geckoboard's api assumes the password will always be X
GECKO_API_PASS = env.str('GECKO_API_PASS', 'X')

ALLOWED_IMAGE_FORMATS = ('PNG', 'JPG', 'JPEG')

# Settings for email to supplier
CONTACT_SUPPLIER_SUBJECT = env.str(
    'CONTACT_SUPPLIER_SUBJECT',
    'Someone is interested in your Find a Buyer profile'
)
CONTACT_SUPPLIER_FROM_EMAIL = env.str('CONTACT_SUPPLIER_FROM_EMAIL')

# Automated email settings
NO_CASE_STUDIES_SUBJECT = env.str(
    'NO_CASE_STUDIES_SUBJECT',
    'Get seen by more international buyers by improving your profile'
)
NO_CASE_STUDIES_DAYS = env.int('NO_CASE_STUDIES_DAYS', 8)
NO_CASE_STUDIES_URL = env.str(
    'NO_CASE_STUDIES_URL',
    'https://find-a-buyer.export.great.gov.uk/company/case-study/edit/'
)
NO_CASE_STUDIES_UTM = env.str(
    'NO_CASE_STUDIES_UTM',
    'utm_source=system mails&utm_campaign=case study creation&utm_medium=email'
)

HASNT_LOGGED_IN_SUBJECT = env.str(
    'HASNT_LOGGED_IN_SUBJECT',
    'Update your Find a buyer profile'
)
HASNT_LOGGED_IN_DAYS = env.int('HASNT_LOGGED_IN_DAYS', 30)

HASNT_LOGGED_IN_URL = env.str(
    'HASNT_LOGGED_IN_URL',
    'https://sso.trade.great.gov.uk/accounts/login/?next={next}'.format(
        next='https://find-a-buyer.export.great.gov.uk/'
    )
)
HASNT_LOGGED_IN_UTM = env.str(
    'HASNT_LOGGED_IN_UTM',
    'utm_source=system emails&utm_campaign=Dormant User&utm_medium=email'
)

VERIFICATION_CODE_NOT_GIVEN_SUBJECT = env.str(
    'VERIFICATION_CODE_NOT_GIVEN_SUBJECT',
    'Please verify your company’s Find a buyer profile',
)
VERIFICATION_CODE_NOT_GIVEN_SUBJECT_2ND_EMAIL = env.str(
    'VERIFICATION_CODE_NOT_GIVEN_SUBJECT',
    VERIFICATION_CODE_NOT_GIVEN_SUBJECT,
)
VERIFICATION_CODE_NOT_GIVEN_DAYS = env.int(
    'VERIFICATION_CODE_NOT_GIVEN_DAYS', 8
)
VERIFICATION_CODE_NOT_GIVEN_DAYS_2ND_EMAIL = env.int(
    'VERIFICATION_CODE_NOT_GIVEN_DAYS_2ND_EMAIL', 16
)
VERIFICATION_CODE_URL = env.str(
    'VERIFICATION_CODE_URL', 'http://great.gov.uk/verify'
)
NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS = env.int(
    'NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS', 7
)
NEW_COMPANIES_IN_SECTOR_SUBJECT = env.str(
    'NEW_COMPANIES_IN_SECTOR_SUBJECT',
    'Find a supplier service - New UK companies in your industry now available'
)
NEW_COMPANIES_IN_SECTOR_UTM = env.str(
    'NEW_COMPANIES_IN_SECTOR_UTM', (
        'utm_source=system%20emails&utm_campaign='
        'Companies%20in%20a%20sector&utm_medium=email'
    )
)
ZENDESK_URL = env.str(
    'ZENDESK_URL',
    'https://contact-us.export.great.gov.uk/feedback/directory/'
)
UNSUBSCRIBED_SUBJECT = env.str(
    'UNSUBSCRIBED_SUBJECT',
    'Find a buyer service - unsubscribed from marketing emails'
)

# Celery
# separate to REDIS_CACHE_URL as needs to start with 'redis' and SSL conf
# is in api/celery.py
CELERY_BROKER_URL = REDIS_CELERY_URL
CELERY_RESULT_BACKEND = REDIS_CELERY_URL
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_TASK_ALWAYS_EAGER = env.bool('CELERY_TASK_ALWAYS_EAGER', False)
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_BROKER_POOL_LIMIT = None

# API CLIENT CORE
DIRECTORY_SSO_API_CLIENT_DEFAULT_TIMEOUT = 15

# SSO API Client
DIRECTORY_SSO_API_CLIENT_BASE_URL = env.str('SSO_API_CLIENT_BASE_URL', '')
DIRECTORY_SSO_API_CLIENT_API_KEY = env.str('SSO_SIGNATURE_SECRET', '')
DIRECTORY_SSO_API_CLIENT_SENDER_ID = env.str(
    'DIRECTORY_SSO_API_CLIENT_SENDER_ID', 'directory'
)

# FAS
FAS_COMPANY_LIST_URL = env.str('FAS_COMPANY_LIST_URL', '')
FAS_COMPANY_PROFILE_URL = env.str('FAS_COMPANY_PROFILE_URL', '')
FAS_NOTIFICATIONS_UNSUBSCRIBE_URL = env.str(
    'FAS_NOTIFICATIONS_UNSUBSCRIBE_URL', ''
)

# FAB
FAB_NOTIFICATIONS_UNSUBSCRIBE_URL = env.str(
    'FAB_NOTIFICATIONS_UNSUBSCRIBE_URL', ''
)
FAB_TRUSTED_SOURCE_ENROLMENT_LINK = env.str(
    'FAB_TRUSTED_SOURCE_ENROLMENT_LINK'
)

# DIRECTORY URLS
DIRECTORY_CONSTANTS_URL_GREAT_DOMESTIC = env.str(
    'DIRECTORY_CONSTANTS_URL_GREAT_DOMESTIC', ''
)

# aws, localhost, or govuk-paas
ELASTICSEARCH_PROVIDER = env.str('ELASTICSEARCH_PROVIDER', 'aws').lower()

if ELASTICSEARCH_PROVIDER == 'govuk-paas':
    services = {
        item['instance_name']: item for item in VCAP_SERVICES['elasticsearch']
    }
    ELASTICSEARCH_INSTANCE_NAME = env.str(
        'ELASTICSEARCH_INSTANCE_NAME',
        VCAP_SERVICES['elasticsearch'][0]['instance_name']
    )
    connections.create_connection(
        alias='default',
        hosts=[services[ELASTICSEARCH_INSTANCE_NAME]['credentials']['uri']],
        connection_class=RequestsHttpConnection,
    )
elif ELASTICSEARCH_PROVIDER == 'localhost':
    connections.create_connection(
        alias='default',
        hosts=['localhost:9200'],
        use_ssl=False,
        verify_certs=False,
        connection_class=RequestsHttpConnection
    )
else:
    raise NotImplementedError()

ELASTICSEARCH_COMPANY_INDEX_ALIAS = env.str(
    'ELASTICSEARCH_COMPANY_INDEX_ALIAS', 'companies-alias'
)

# Activity Stream
ACTIVITY_STREAM_ACCESS_KEY_ID = env.str('ACTIVITY_STREAM_ACCESS_KEY_ID', '')
ACTIVITY_STREAM_SECRET_ACCESS_KEY = env.str(
    'ACTIVITY_STREAM_SECRET_ACCESS_KEY', ''
)
ACTIVITY_STREAM_IP_WHITELIST = env.list('ACTIVITY_STREAM_IP_WHITELIST')

# Export opportunity lead generation
SUBJECT_EXPORT_OPPORTUNITY_CREATED = env.str(
    'SUBJECT_EXPORT_OPPORTUNITY_CREATED',
    'A new Export Opportunity lead has been submitted via great.gov.uk'
)
ITA_EMAILS_FOOD_IS_GREAT_FRANCE = env.list(
    'ITA_EMAILS_FOOD_IS_GREAT_FRANCE', default=[]
)
ITA_EMAILS_FOOD_IS_GREAT_SINGAPORE = env.list(
    'ITA_EMAILS_FOOD_IS_GREAT_SINGAPORE', default=[]
)

ITA_EMAILS_LEGAL_IS_GREAT_FRANCE = env.list(
    'ITA_EMAILS_LEGAL_IS_GREAT_FRANCE', default=[]
)
ITA_EMAILS_LEGAL_IS_GREAT_SINGAPORE = env.list(
    'ITA_EMAILS_LEGAL_IS_GREAT_SINGAPORE', default=[]
)

# Healthcheck
DIRECTORY_HEALTHCHECK_TOKEN = env.str('HEALTH_CHECK_TOKEN')
DIRECTORY_HEALTHCHECK_BACKENDS = [
    directory_healthcheck.backends.SingleSignOnBackend,
    healthcheck.backends.ElasticSearchCheckBackend,
    # health_check.db.backends.DatabaseBackend and
    # health_check.cache.CacheBackend are also registered in
    # INSTALLED_APPS's health_check.db and health_check.cache
]

CSV_DUMP_AUTH_TOKEN = env.str('CSV_DUMP_AUTH_TOKEN')
BUYERS_CSV_FILE_NAME = 'find-a-buyer-buyers.csv'
SUPPLIERS_CSV_FILE_NAME = 'find-a-buyer-suppliers.csv'

FEATURE_SKIP_MIGRATE = env.bool('FEATURE_SKIP_MIGRATE', False)
FEATURE_REDIS_USE_SSL = env.bool('FEATURE_REDIS_USE_SSL', False)
FEATURE_TEST_API_ENABLED = env.bool('FEATURE_TEST_API_ENABLED', False)
FEATURE_FLAG_ELASTICSEARCH_REBUILD_INDEX = env.bool(
    'FEATURE_FLAG_ELASTICSEARCH_REBUILD_INDEX', True
)
FEATURE_VERIFICATION_LETTERS_ENABLED = env.bool(
    'FEATURE_VERIFICATION_LETTERS_ENABLED', False
)
FEATURE_REGISTRATION_LETTERS_ENABLED = env.bool(
    'FEATURE_REGISTRATION_LETTERS_ENABLED', False
)
# If enabled sends via govenotify else uses stannp
FEATURE_VERIFICATION_LETTERS_VIA_GOVNOTIFY_ENABLED = env.bool(
    'FEATURE_VERIFICATION_LETTERS_VIA_GOVNOTIFY_ENABLED', False
)
FEATURE_MANUAL_PUBLISH_ENABLED = env.bool(
    'FEATURE_MANUAL_PUBLISH_ENABLED', False
)

# directory-signature-auth
SIGNATURE_SECRET = env.str('SIGNATURE_SECRET')
SIGAUTH_URL_NAMES_WHITELIST = [
    'activity-stream',
    'gecko-total-registered-suppliers',
    'health-check-database',
    'health-check-cache',
    'health-check-single-sign-on',
    'health-check-elastic-search',
    'health-check-ping',
]
if STORAGE_CLASS_NAME == 'local-storage':
    SIGAUTH_URL_NAMES_WHITELIST.append('media')

RESTRICT_ADMIN = env.bool('IP_RESTRICTOR_RESTRICT_IPS', False)
ALLOWED_ADMIN_IPS = env.list('IP_RESTRICTOR_ALLOWED_ADMIN_IPS', default=[])
ALLOWED_ADMIN_IP_RANGES = env.list(
    'IP_RESTRICTOR_ALLOWED_ADMIN_IP_RANGES', default=[]
)
RESTRICTED_APP_NAMES = env.list(
    'IP_RESTRICTOR_RESTRICTED_APP_NAMES', default=['admin']
)

SOLE_TRADER_NUMBER_SEED = env.int('SOLE_TRADER_NUMBER_SEED')

# directory constants
DIRECTORY_CONSTANTS_URL_EXPORT_READINESS = env.str(
    'DIRECTORY_CONSTANTS_URL_EXPORT_READINESS', ''
)

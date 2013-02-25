import os
from os.path import join

MANAGERS = ADMINS = (
    ('Andrei', 'ak@ak-desktop.org'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',                      # Or path to database file if using sqlite3.
        'USER': 'postgres',                      # Not used with sqlite3.
        'PASSWORD': 'postgres',                  # Not used with sqlite3.
        'HOST': '',
        'PORT': '',
    }
}

FROM_ADDRESS            = 'ak@ak-desktop.org'
DEFAULT_FROM_EMAIL      = 'ak@ak-desktop.org'
DEBUG                   = True
TEMPLATE_DEBUG          = True

EMAIL_BACKEND           = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST              = 'localhost'
EMAIL_PORT              = 25
EMAIL_HOST_USER         = ''
EMAIL_HOST_PASSWORD     = ''

SAVE_ON_TOP             = True
TIME_ZONE               = 'America/New_York'  # http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
LANGUAGE_CODE           = 'en-us'         # http://www.i18nguy.com/unicode/language-identifiers.html
SITE_ID                 = 1
USE_I18N                = True
USE_L10N                = True

ACCOUNT_ACTIVATION_DAYS = 2

SITE_ROOT               = '~/pytut/dbe/'
MEDIA_ROOT              = '/home/ak/pytut/dbe/media/'
MEDIA_URL               = 'http://localhost:8001/media/'
STATIC_ROOT             = '/home/ak/Downloads/Django-1.5c1/django/contrib/admin/static/'
STATIC_URL              = 'http://localhost:8001/static/'
SECRET_KEY              = 'i02p@*@*3&(434gc1n80z^hu8g09mfbsi^+%ylo5$&jrusg^h5'
ROOT_URLCONF            = 'dbe.urls'
INTERNAL_IPS            = ['127.0.0.1']
DEBUG_TOOLBAR_CONFIG    = {'INTERCEPT_REDIRECTS' : False}
# LOGIN_URL            = '/admin'

TEMPLATE_LOADERS = (
    'hamlpy.template.loaders.HamlPyFilesystemLoader',
    'hamlpy.template.loaders.HamlPyAppDirectoriesLoader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

TEMPLATE_DIRS = (
    join(SITE_ROOT, 'templates'),
    join(SITE_ROOT, 'templates/myapp'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'dbe.forum.views.forum_context',
    'dbe.portfolio.views.portfolio_context',
    'dbe.cal.views.cal_context',
    'dbe.sb.views.sbcontext',
    'dbe.store9.views.cart_processor',
    # 'dbe.photo.views.photo_context',
)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'south',
    'registration',
]

try:
    from local_settings import *
except Exception, e:
    print e
    pass

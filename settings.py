from django.conf import global_settings
import locale
# Django settings for biereapp project.

base_path = "/Users/marc/Dropbox/Projects/"

app_root = base_path + "biereapp/"

# Django settings for io project.
import sys
sys.path.insert(0, base_path);

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Marc Boivin', 'mjsdesign@gmail.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'django.db.backends.sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'biereapp.sql'             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Montreal'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'fr_CA'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = app_root + 'frontend/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://localhost:8000/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '%i!f*5_+pqy^=m-&z$3in7$qn(yz8laz!lnfn0ewul9(l1np3!'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'biereapp.middleware.GlobalUser',
)

ROOT_URLCONF = 'biereapp.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    app_root + 'frontend/templates/',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.humanize',
    'biereapp',
)

# Tempalte tags
TEMPLATE_TAGS = ( "biereapp.templatetags.extras", ) 

UPLOAD_FOLDER = 'upload/'

MEDIA_PATHS = {
        u'MEDIA' : MEDIA_URL,
        u'JQUERY' : MEDIA_URL+"jquery/",
        u'CSS' : MEDIA_URL+"css/",
        u'JS' : MEDIA_URL + "js/",
        u'MIME-TYPE': MEDIA_URL + "mime_type/",
        u'UPLOAD': MEDIA_URL + UPLOAD_FOLDER
}

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'mjsdesign@gmail.com'
EMAIL_HOST_PASSWORD = '1nf0d3v.c@'
EMAIL_PORT = 587

FILE_UPLOAD_PERMISSIONS = 0744

CACHE_BACKEND = 'file:///tmp/django_cache'

"""Kind of a hack right now, but we set the locales based on 
the language code caus Django doesn't seem to do it. Morrons"""
locale.setlocale(locale.LC_ALL, LANGUAGE_CODE)

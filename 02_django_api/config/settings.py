import os
from pathlib import Path

from dotenv import load_dotenv
from split_settings.tools import include

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = True
DEBUG = os.environ.get('DEBUG', '').lower() in {'true', 'on', '1'}

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
ALLOWED_HOSTS = [] if not any(ALLOWED_HOSTS) else ALLOWED_HOSTS

include(
    'components/installed_apps.py',
)

include(
    'components/middleware.py',
)

ROOT_URLCONF = 'config.urls'

include(
    'components/templates.py',
)

WSGI_APPLICATION = 'config.wsgi.application'

include(
    'components/database.py',
)

include(
    'components/auth_password_validators.py',
)


LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOCALE_PATH = ['movies/locale']

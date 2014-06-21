# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

ADMINS = (
    ('', ''),
)
MANAGERS = ADMINS

SECRET_KEY = 'thisisnotasecret'

ALLOWED_HOSTS = ['']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

GOOGLEAUTH_CLIENT_ID = ''
GOOGLEAUTH_CLIENT_SECRET = ''
GOOGLEAUTH_CALLBACK_DOMAIN = ''
GOOGLEAUTH_IS_STAFF = True
# GOOGLEAUTH_APPS_DOMAIN = ''  # to limit access to a single Google Apps domain

AWS_KEY = ''
AWS_SECRET = ''

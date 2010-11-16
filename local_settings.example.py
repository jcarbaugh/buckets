DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

AWS_KEY = ''
AWS_SECRET = ''

MEDIASYNC = {
    'BACKEND': 'mediasync.backends.s3',
    'AWS_KEY': AWS_KEY,
    'AWS_SECRET': AWS_SECRET,
    'AWS_BUCKET': "",
    'AWS_PREFIX': "",
    #'CACHE_BUSTER': 1234567890,
    'DOCTYPE': 'html5',
}

GOOGLEAUTH_DOMAIN = ''
GOOGLEAUTH_REALM = ''

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.environ.get('POSTGRES_DB', 'movies_database'),
        'USER': os.environ.get('POSTGRES_USER', 'app'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', '123qwe'),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', 5432),
        'OPTIONS': {
            # Нужно явно указать схемы, с которыми будет работать приложение.
           'options': '-c search_path=public,content'
        }
    }
}

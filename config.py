import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True        
    SECRETS_FILE = os.environ.get('SECRETS_FILE', '/usr/src/instance/client_secrets.json')
    CREDENTIALS_FILE = os.environ.get('CREDENTIALS_FILE', '/usr/src/instance/credentials.json')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:////usr/src/app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class ProdConfig(Config):
    DEBUG = False

class TestConfig(Config):
    TESTING = True

class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


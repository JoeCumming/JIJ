import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True        
    SECRETS_FILE = os.environ.get('SECRETS_FILE', './instance/client_secrets.json')
    CREDENTIALS_FILE = os.environ.get('CREDENTIALS_FILE', './instance/credentials.json')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
    CELERY_BROKER_URL = REDIS_URL
    RESULT_BACKEND = REDIS_URL
    
    @staticmethod
    def init_app(app):
        pass

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

config = {
    'development': DevConfig,
    'testing': TestConfig,
    'production': ProdConfig,
    'staging': StagingConfig,    
    'default': DevConfig
}
class BaseConfig(object):
    DEBUG = True
    MONGO_URI = 'mongodb://localhost:3012/movies_api'
    JWT_SECRET_KEY = 'secret'
    TESTING = False

class TestConfig(BaseConfig):
    DEBUG = True
    MONGO_URI = 'mongodb://localhost:3012/movies_api_test'
    TESTING = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False

class DevelopmentConfig(BaseConfig):
    DEBUG = True

class ProductionConfig(BaseConfig):
    DEBUG = False
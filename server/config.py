class BaseConfig(object):
    DEBUG = True
    MONGO_URI = 'mongodb://localhost:3012/movies_api'
    JWT_SECRET_KEY = 'secret'
    TESTING = False


class TestConfig(BaseConfig):
    DEBUG = True
    MONGO_URI = 'mongodb://localhost:3012/movies_api_test'
    JWT_SECRET_KEY = 'secret'
    TESTING = True


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False
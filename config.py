

class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    DEBUG = True
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300


class TestingConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    TESTING = True
    CACHE_TYPE = 'SimpleCache'
    
class ProductionConfig:
    pass
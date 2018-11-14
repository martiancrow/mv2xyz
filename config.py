import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'hard to guess string'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'stmp.mv2.xyz')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = 'lxl@mv2.xyz'
    MAIL_PASSWORD = 'Stevenloveme7'
    WEB_HOST = 'http://127.0.0.1:5000'
    FLASKY_MAIL_SUBJECT_PREFIX = '[mv2 记事本]'
    FLASKY_MAIL_SENDER = 'mv2 管理员 <lxl@mv2.xyz>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'mysql+mysqlconnector://admin:admin!@#@192.168.1.127/mv2xyz.dev?charset=utf8mb4&collation=utf8mb4_general_ci'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'mysql+mysqlconnector://admin:admin!@#@192.168.1.127/mv2xyz.test?charset=utf8mb4&collation=utf8mb4_general_ci'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+mysqlconnector://admin:admin!@#@192.168.1.127/mv2xyz?charset=utf8mb4&collation=utf8mb4_general_ci'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}

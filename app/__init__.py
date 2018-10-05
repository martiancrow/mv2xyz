from flask import Flask
from flask_bootstrap import Bootstrap, WebCDN, ConditionalCDN, BOOTSTRAP_VERSION, JQUERY_VERSION, HTML5SHIV_VERSION, RESPONDJS_VERSION
from flask_mail import Mail
from flask_moment import Moment
from flask_pagedown import PageDown
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def change_cdn_domestic(tar_app):
    static = tar_app.extensions['bootstrap']['cdns']['static']
    local = tar_app.extensions['bootstrap']['cdns']['local']

    def change_one(tar_lib, tar_ver, fallback):
        if 'bootstrap' in tar_lib:
            tar_lib = 'twitter-bootstrap'
    
        tar_js = ConditionalCDN('BOOTSTRAP_SERVE_LOCAL', fallback, WebCDN('//cdn.staticfile.org/' + tar_lib + '/' + tar_ver + '/'))
        tar_app.extensions['bootstrap']['cdns'][tar_lib] = tar_js

    libs = {'jquery': {'ver': JQUERY_VERSION, 'fallback': local},
            'bootstrap': {'ver': BOOTSTRAP_VERSION, 'fallback': local},
            'html5shiv': {'ver': HTML5SHIV_VERSION, 'fallback': static},
            'respond.js': {'ver': RESPONDJS_VERSION, 'fallback': static}}

    for lib, par in libs.items():
        change_one(lib, par['ver'], par['fallback'])



def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    pagedown.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_message = "请先登录"

    change_cdn_domestic(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .user import user as user_blueprint
    app.register_blueprint(user_blueprint, url_prefix='/user')
    
    from .test import test as test_blueprint
    app.register_blueprint(test_blueprint, url_prefix='/test')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    
    return app

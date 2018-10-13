import time
import base64
import struct
from datetime import datetime, timedelta
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request, after_this_request
from flask_login import UserMixin, AnonymousUserMixin, login_user
from sqlalchemy.dialects.mysql import VARBINARY
from .. import db, login_manager

COOKIE_NAME = 'remember_token'
COOKIE_DURATION = timedelta(days=365)
COOKIE_SECURE = None
COOKIE_HTTPONLY = False

class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE = 0x04
    MODERATE = 0x08
    ADMIN = 0x10

class ua_user(db.Model):
    __tablename__ = 'ua_users'
    ua_user_id = db.Column(db.Integer, primary_key=True)
    ua_user_email = db.Column(db.String(128), unique=True, index=True)
    ua_user_nick = db.Column(db.String(64), unique=True, index=True)
    ua_pwd_hash = db.Column(db.String(128))
    ua_email_confirmed = db.Column(db.Boolean, default=False)
    ua_createtime = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship('res_post', backref='author', lazy='dynamic', cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super(ua_user, self).__init__(**kwargs)

        if self.ua_user_email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.ua_pwd_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.ua_pwd_hash, password)

    def generate_confirmation_email_token(self, expiration=7200):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.ua_user_id}).decode('utf-8')

    def confirm_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])

        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False

        if data.get('confirm') != self.ua_user_id:
            return False

        self.ua_email_confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def generate_reset_pwd_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.ua_user_id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])

        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False

        user = ua_user.query.get(data.get('reset'))

        if user is None:
            return False

        user.password = new_password
        db.session.add(user)
        return True

    def gravatar_hash(self):
        return hashlib.md5(self.ua_user_email.lower().encode('utf-8')).hexdigest()

    def gravatar(self, size=100, default='identicon', rating='g'):
        url = 'https://secure.gravatar.com/avatar'
        hash = self.avatar_hash or self.gravatar_hash()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def __repr__(self):
        return '<ua_user %r>' % self.ua_user_nick

class ua_session(db.Model):
    __tablename__ = 'ua_session_base'
    ua_sb_key = db.Column(db.String(256), primary_key=True)
    ua_sb_ip = db.Column(db.String(128))
    user_id = db.Column(db.Integer)
    ua_sb_exceed = db.Column(db.SmallInteger, default=7200)
    ua_sb_lastheart = db.Column(db.BigInteger, default=time.time)
    ua_sb_createtime = db.Column(db.BigInteger, default=time.time)
    ua_sd_datas = db.relationship('ua_session_data', backref='base', lazy='dynamic', cascade="all, delete-orphan")


    def __init__(self, **kwargs):
        super(ua_session, self).__init__(**kwargs)

        if 'ua_sb_key' not in kwargs:
            key = generate_password_hash(str(time.time())).replace('pbkdf2:sha256:50000$', '')
            self.ua_sb_key = key

    @property
    def datas(self):
        sess_datas = {}
        for item in self.ua_sd_datas:
            if item.ua_sd_type == 'int':
                sess_datas[item.ua_sd_key] = struct.unpack('i', item.ua_sd_value)[0]

            elif item.ua_sd_type == 'str':
                sess_datas[item.ua_sd_key] = item.ua_sd_value.decode()

            else:
                sess_datas[item.ua_sd_key] = item.ua_sd_value

        return sess_datas

    def set_data(self, key, val):
        ud = ua_session_data.query.filter_by(ua_sb_key=self.ua_sb_key, ua_sd_key=key).first()

        val_type = 'bytes'

        if isinstance(val, int):
            val = struct.pack('i', val)
            val_type = 'int'

        elif isinstance(val, str):
            val = val.encode()
            val_type = 'str'

        if ud == None and val != None:
            ud = ua_session_data(ua_sb_key=self.ua_sb_key, ua_sd_key=key, ua_sd_value=val, ua_sd_type=val_type)
            db.session.add(ud)
            db.session.commit()

        elif ud != None and val == None:
            db.session.delete(ud)
            db.session.commit()

        elif ud != None and val != None:
            ud.ua_sd_value = val
            db.session.add(ud)
            db.session.commit()

    def is_exceed(self):
        return self.ua_sb_exceed < (int(time.time()) - self.ua_sb_lastheart)

    def __repr__(self):
        return '<ua_session %r>' % self.ua_sb_key

class ua_session_data(db.Model):
    __tablename__ = 'ua_session_data'
    ua_sb_key = db.Column(db.String(128), db.ForeignKey('ua_session_base.ua_sb_key'), primary_key=True)
    ua_sd_key = db.Column(db.String(64), primary_key=True)
    ua_sd_value = db.Column(VARBINARY(512))
    ua_sd_type = db.Column(db.String(8))


    def __init__(self, **kwargs):
        super(ua_session_data, self).__init__(**kwargs)

    def __repr__(self):
        return '<ua_session_data %r>' % self.ua_sd_key


class User(UserMixin):

    def __init__(self, sess, user_id, stophreat=False, **kwargs):
        self.id = sess.ua_sb_key
        self.sess = sess

        if self.sess == None:
            self.user = None
        else:
            self.sess.user_id = user_id
            db.session.add(self.sess)
            db.session.commit()

            self.user = ua_user.query.get(self.sess.user_id)

        if not stophreat:
            self.sess.ua_sb_lastheart = time.time()
            db.session.add(self.sess)
            db.session.commit()
    
    @property
    def datas(self):
        return self.sess.datas

    def set_data(self, key, val):
        self.sess.set_data(key, val)

    def logout(self):
        self.user = None
        db.session.delete(self.sess)
        db.session.commit()

    def get_auth_token(self):
        return self.id
       

class AnonymousUser(AnonymousUserMixin):

    def __init__(self, stophreat=False, **kwargs):

        cookie_name = current_app.config.get('REMEMBER_COOKIE_NAME', COOKIE_NAME)

        if cookie_name not in request.cookies:
            self.sess = ua_session(ua_sb_ip=request.remote_addr)
            self.id = self.sess.ua_sb_key
            db.session.add(self.sess)
            db.session.commit()

            @after_this_request
            def _set_cookie(response):
                # cookie settings
                cookie_name = current_app.config.get('REMEMBER_COOKIE_NAME', COOKIE_NAME)
                duration = current_app.config.get('REMEMBER_COOKIE_DURATION', COOKIE_DURATION)
                domain = current_app.config.get('REMEMBER_COOKIE_DOMAIN')
                path = current_app.config.get('REMEMBER_COOKIE_PATH', '/')

                secure = current_app.config.get('REMEMBER_COOKIE_SECURE', COOKIE_SECURE)
                httponly = current_app.config.get('REMEMBER_COOKIE_HTTPONLY', COOKIE_HTTPONLY)

                data = self.id
                expires = datetime.utcnow() + duration

                # actually set it
                response.set_cookie(cookie_name,
                                    value=data,
                                    expires=expires,
                                    domain=domain,
                                    path=path,
                                    secure=secure,
                                    httponly=httponly)

                return response
            

        else:
            key = request.cookies[cookie_name]
            self.sess = ua_session.query.get(key)

            if self.sess == None:
                self.sess = ua_session(ua_sb_key=key, ua_sb_ip=request.remote_addr)
                db.session.add(self.sess)
                db.session.commit()

            self.id = key

        if not stophreat:
            self.sess.ua_sb_lastheart = time.time()
            db.session.add(self.sess)
            db.session.commit()

    @property
    def datas(self):
        return self.sess.datas

    def set_data(self, key, val):
        self.sess.set_data(key, val)

    def clear(self):
        db.session.delete(self.sess)
        db.session.commit()

    def get_auth_token(self):
        return self.id

    def reset_lastseen(self):
        self.sess.ua_sb_lastheart = time.time()
        db.session.add(self.sess)
        db.session.commit()


login_manager.anonymous_user = AnonymousUser

@login_manager.token_loader
def load_token(key):
    sess = ua_session.query.get(key)

    if sess:

        if sess.user_id is not None:

            return User(sess, sess.user_id)

    return None

@login_manager.user_loader
def load_user(key):
    sess = ua_session.query.get(key)

    if sess:

        if sess.user_id is not None:

            return User(sess, sess.user_id)

    return None

@login_manager.request_loader
def load_request(request):

    username = request.args.get('username')
    password = request.args.get('password')

    if username and password:
        user = ua_user.query.filter_by(email=username)

        if user is not None and user.verify_password(password):

            sess = ua_session.query.filter_by(user_id=user.ua_user_id)

            if sess:
                db.session.delete(sess)
                db.session.commit()

            sess = ua_session(ua_sb_ip=request.remote_addr)
        
            return User(sess, user.ua_user_id, True)


    auth_token = request.headers.get('Authorization')

    if auth_token:
        auth_token = auth_token.replace('Basic ', '', 1)

        try:
            auth_token = base64.b64decode(auth_token)

        except TypeError:
            pass

        sess = ua_session.query.get(auth_token)

        if sess:

            if not sess.is_exceed:

                if ua_user.query.get(sess.user_id):

                    return User(sess, sess.user_id, True)
        
    
    return AnonymousUser(True)



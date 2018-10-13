import time
import base64
import struct
import bleach
from markdown import markdown
from datetime import datetime, timedelta
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request, after_this_request
from sqlalchemy.dialects.mysql import LONGBLOB, LONGTEXT
from .. import db, login_manager

class res_postclass(db.Model):
    __tablename__ = 'res_postclasses'
    postclass_id = db.Column(db.Integer, primary_key=True)
    postclass_uid = db.Column(db.Integer, db.ForeignKey('ua_users.ua_user_id'))
    postclass_name = db.Column(db.String(128))
    postclass_createtime = db.Column(db.DateTime(), default=datetime.utcnow)

    def __init__(self, **kwargs):
        super(res_postclass, self).__init__(**kwargs)

    
    def __repr__(self):
        return '<res_postclass %r>' % self.postclass_name

class res_post(db.Model):
    __tablename__ = 'res_posts'
    post_id = db.Column(db.Integer, primary_key=True)
    post_pid = db.Column(db.Integer, db.ForeignKey('res_posts.post_id'), default=0)
    post_cid = db.Column(db.Integer, db.ForeignKey('res_postclasses.postclass_id'), default=0)
    author_id = db.Column(db.Integer, db.ForeignKey('ua_users.ua_user_id'))
    post_name = db.Column(db.String(64))
    post_body_md = db.Column(LONGTEXT)
    post_body_html = db.Column(LONGTEXT)
    post_updatetime = db.Column(db.DateTime(), default=datetime.utcnow)
    post_createtime = db.Column(db.DateTime(), default=datetime.utcnow)
    chilposts = db.relationship('res_post', lazy='dynamic', cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super(res_post, self).__init__(**kwargs)
        self.post_updatetime = datetime.utcnow()

    @property
    def parentpost(self):
        if self.post_id:
            return res_post.query.get(self.post_pid)
        else:
            return None

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        '''
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img']

        allowed_attrs = (
                    '*': ['class'],
                    'a': ['href', 'rel'],
                    'img': ['alt'],)

        
        target.post_body_html = bleach.linkify(
                                bleach.clean(
                                    markdown(value, output_format='html'), tags=allowed_tags, attributes=allowed_attrs, strip=True))
        
        '''
        
        target.post_body_html = markdown(value, output_format='html')

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        for i in range(count):
            p = res_post(post_name=forgery_py.lorem_ipsum.title(),
                    post_body_md=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                    post_updatetime=forgery_py.date.date(True),
                    post_creattime=forgery_py.date.date(True),
                    author_id=1)
            db.session.add(p)
            db.session.commit()

    def __repr__(self):
        return '<res_post %r>' % self.ua_user_nick

db.event.listen(res_post.post_body_md, 'set', res_post.on_changed_body)

class res_file(db.Model):
    __tablename__ = 'res_files'
    file_id = db.Column(db.Integer, primary_key=True)
    file_uid = db.Column(db.Integer, db.ForeignKey('ua_users.ua_user_id'))
    file_name = db.Column(db.String(128))
    file_type = db.Column(db.String(64))
    file_data = db.Column(LONGBLOB)
    file_isextern = db.Column(db.Boolean, default=False)
    file_uri = db.Column(db.String(512))
    file_createtime = db.Column(db.DateTime(), default=datetime.utcnow)

    def __init__(self, **kwargs):
        super(res_file, self).__init__(**kwargs)

    
    def __repr__(self):
        return '<res_file %r>' % self.file_name
        




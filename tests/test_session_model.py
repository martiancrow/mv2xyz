import unittest
import time
from datetime import datetime
from app import create_app, db
from app.models.ua_models import ua_user, ua_session, ua_session_data


class sessionModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_sess_creat(self):
        sess = ua_session(ua_sb_ip='127.0.0.1')
        db.session.add(sess)
        db.session.commit()

        self.assertTrue(ua_session.query.get(sess.ua_sb_key) != None)

    def test_sess_creatsetkey(self):
        sess = ua_session(ua_sb_key='test', ua_sb_ip='127.0.0.1')
        db.session.add(sess)
        db.session.commit()

        self.assertTrue(ua_session.query.get('test') != None)

    def test_sess_addstr(self):
        sess = ua_session(ua_sb_ip='127.0.0.1')
        db.session.add(sess)
        db.session.commit()

        sess.set_data('key1', '中文')

        self.assertTrue(sess.datas['key1'] == '中文')

    def test_sess_addint(self):
        sess = ua_session(ua_sb_ip='127.0.0.1')
        db.session.add(sess)
        db.session.commit()

        sess.set_data('key2', 10)

        self.assertTrue(sess.datas['key2'] == 10)

    def test_sess_del(self):
        sess = ua_session(ua_sb_key='test', ua_sb_ip='127.0.0.1')
        db.session.add(sess)
        db.session.commit()

        sess.set_data('key1', 'val1')
        get = (sess.datas['key1'] == 'val1')

        sess.set_data('key1', None)
        ud = ua_session_data.query.filter_by(ua_sb_key='test', ua_sd_key='key1').first()
        sdel = (ud == None)

        self.assertTrue(get and sdel)

    def test_sess_update(self):
        sess = ua_session(ua_sb_key='test', ua_sb_ip='127.0.0.1')
        db.session.add(sess)
        db.session.commit()

        sess.set_data('key1', 'val1')
        get = (sess.datas['key1'] == 'val1')

        sess.set_data('key1', 'val2')
        update = (sess.datas['key1'] == 'val2')

        self.assertTrue(get and update)

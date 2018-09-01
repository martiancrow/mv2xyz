import unittest
import time
from datetime import datetime
from app import create_app, db
from app.models.ua_models import ua_user
'''
class userModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = ua_user(password='cat')
        self.assertTrue(u.ua_pwd_hash is not None)

    def test_no_password_getter(self):
        u = ua_user(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = ua_user(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = ua_user(password='cat')
        u2 = ua_user(password='cat')
        self.assertTrue(u.ua_pwd_hash != u2.ua_pwd_hash)

    def test_valid_confirmation_token(self):
        u = ua_user(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_email_token()
        self.assertTrue(u.confirm_email(token))

    def test_invalid_confirmation_token(self):
        u1 = ua_user(password='cat')
        u2 = ua_user(password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_confirmation_email_token()
        self.assertFalse(u2.confirm_email(token))

    def test_expired_confirmation_token(self):
        u = ua_user(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_email_token(1)
        time.sleep(2)
        self.assertFalse(u.confirm_email(token))

    def test_valid_reset_token(self):
        u = ua_user(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_pwd_token()
        self.assertTrue(ua_user.reset_password(token, 'dog'))
        self.assertTrue(u.verify_password('dog'))

    def test_invalid_reset_token(self):
        u = ua_user(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_pwd_token()
        self.assertFalse(ua_user.reset_password(token + 'a', 'horse'))
        self.assertTrue(u.verify_password('cat'))


    def test_gravatar(self):
        u = ua_user(ua_user_email='john@example.com', password='cat')
        with self.app.test_request_context('/'):
            gravatar = u.gravatar()
            gravatar_256 = u.gravatar(size=256)
            gravatar_pg = u.gravatar(rating='pg')
            gravatar_retro = u.gravatar(default='retro')
        self.assertTrue('https://secure.gravatar.com/avatar/' +
                        'd4c74594d841139328695756648b6bd6'in gravatar)
        self.assertTrue('s=256' in gravatar_256)
        self.assertTrue('r=pg' in gravatar_pg)
        self.assertTrue('d=retro' in gravatar_retro)
'''
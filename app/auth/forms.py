from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models.ua_models import ua_user

class LoginForm(FlaskForm):
    email = StringField('', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('', validators=[DataRequired()])
    submit = SubmitField('登录')

class RegistrationForm(FlaskForm):
    email = StringField('电子邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    nick = StringField('用户昵称', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('用户密码', validators=[DataRequired(), EqualTo('password2', message='两次密码不相同')])
    password2 = PasswordField('重复密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if ua_user.query.filter_by(ua_user_email=field.data).first():
            raise ValidationError('邮箱已被注册')

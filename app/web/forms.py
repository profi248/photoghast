from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(),
                                                   Length(max=255)],
                           render_kw={"placeholder": "username"})

    passwd = PasswordField('password', validators=[DataRequired(),
                                                   Length(max=255)],
                           render_kw={"placeholder": "password"})

    remember = BooleanField('remember me')


class AddUserForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(),
                                                   Length(max=255, min=3)],
                           render_kw={"placeholder": "username"})

    passwd = PasswordField('password', validators=[DataRequired(),
                                                   Length(max=255)],
                           render_kw={"placeholder": "password"})

    admin = BooleanField('admin permissions')


class ChangePasswordForm(FlaskForm):
    old_passwd = PasswordField('old password', validators=[DataRequired(),
                                                           Length(max=255)],
                               render_kw={"placeholder": "old password"})
    new_passwd = PasswordField('new password', validators=[DataRequired(),
                                                           Length(max=255)],
                               render_kw={"placeholder": "new password"})
    new_passwd_repeat = PasswordField('new password again',
                                      validators=[DataRequired(),
                                                  Length(max=255)],
                                      render_kw={"placeholder":
                                                 "new password again"})

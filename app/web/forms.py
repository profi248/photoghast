from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()], render_kw={"placeholder": "username"})
    passwd = PasswordField('password', validators=[DataRequired()],  render_kw={"placeholder": "password"})
    remember = BooleanField('remember me')

import flask
import flask_login
import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker

import utils
import forms
import user_manager
import utils.config as config
from utils.db_models import *


app = flask.Flask(__name__)
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = config.secret

db_engine = sql.create_engine(config.db_uri, echo=False)
Session = sessionmaker(bind=db_engine)
db_session = Session()

@app.route('/')
def index():
    print(flask_login.current_user)
    return flask.render_template('index.html', current_user=flask_login.current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = user_manager.UserManager()
        flask_login.login_user(user)

        flask.flash('Logged in successfully.')

        redir = flask.request.args.get('redir')

        if not utils.is_safe_url(redir):
            return flask.abort(400)

        return flask.redirect(redir or flask.url_for('index'))
    return flask.render_template('login.html', form=form)

@app.route('/logout', methods=['POST'])
def logout():
    flask_login.logout_user()
    flask.flash('Logged out successfully.')
    return flask.redirect(flask.url_for('index'))

@login_manager.user_loader
def load_user(user_id):
    return user_manager.get_user(user_id)


if __name__ == '__main__':
    app.run()

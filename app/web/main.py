import io

import flask
import flask_login

import web_utils
import forms
import user_manager
import utils.config as config
import utils.db_models as models
from utils.common import get_db_session

app = flask.Flask(__name__)
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = config.secret


@app.route('/', methods=['GET'])
def index():
    if flask_login.current_user.is_authenticated:
        db_session = get_db_session()
        images = db_session.query(models.Image.id, models.Image.name).all()
        return flask.render_template('library.html', current_user=flask_login.current_user, images=images)
    else:
        return flask.render_template('index.html', current_user=flask_login.current_user)

@app.route('/thumb/<int:img_id>', methods=['GET'])
@flask_login.login_required
def thumb(img_id):
    db_session = get_db_session()
    img_db = db_session.query(models.Image).filter(models.Image.id == img_id).one_or_none()
    if not img_db:
        return flask.abort(404)

    bytestream = io.BytesIO(img_db.thumbnail)
    return flask.send_file(bytestream, mimetype="image/jpeg",
                           last_modified=img_db.mtime, cache_timeout=config.cache_max_sec)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            username = flask.request.form["username"]
            passwd = flask.request.form["passwd"]
        except KeyError:
            return flask.abort(400)

        try:
            remember = flask.request.form["remember"]
        except KeyError:
            remember = False

        user = user_manager.login(username, passwd)
        if user:
            user = user_manager.UserManager(user)
            flask_login.login_user(user, remember=remember)
        else:
            flask.flash('Username or password is incorrect.')
            return flask.render_template('login.html', form=form, current_user=flask_login.current_user)

        redir = flask.request.args.get('redir')

        if not web_utils.is_safe_url(redir):
            return flask.abort(400)

        return flask.redirect(redir or flask.url_for('index'))

    return flask.render_template('login.html', form=form, current_user=flask_login.current_user)

@app.route('/logout', methods=['POST'])
def logout():
    flask_login.logout_user()
    flask.flash('Logged out successfully.')
    return flask.redirect(flask.url_for('index'))

@login_manager.user_loader
def load_user(user_id):
    return user_manager.get_user(user_id)

@app.after_request
def modify_cache(r):
    r.headers['Cache-Control'] = 'private'
    return r


if __name__ == '__main__':
    app.run()

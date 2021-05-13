import flask
import flask_login
import io
import os

import web_utils
import forms
import user_manager
import utils.config as config
import utils.db_models as models
from utils.common import *

app = flask.Flask(__name__)
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = config.secret


@app.route('/', methods=['GET'])
def index():
    if flask_login.current_user.is_authenticated:
        db_session = get_db_session()
        images = db_session.query(models.Image.id, models.Image.name,
                                  models.Image.thumb_width,
                                  models.Image.thumb_height,
                                  models.Image.width, models.Image.height) \
            .order_by(models.Image.creation.desc()).all()
        return flask.render_template('library.html',
                                     current_user=flask_login.current_user,
                                     images=images)
    else:
        return flask.render_template('index.html',
                                     current_user=flask_login.current_user)


@app.route('/places', methods=['GET'])
@flask_login.login_required
def places():
    db_session = get_db_session()
    places_list = db_session.query(models.Place.id, models.Place.name).all()
    thumb_pics_ids = {}
    for place_db in places_list:
        thumb_pics_ids[place_db.id] = db_session.query(models.Image.id) \
            .filter(models.Image.place_id == place_db.id).first().id

    return flask.render_template('places.html', places=places_list,
                                 current_user=flask_login.current_user,
                                 thumb_pics_ids=thumb_pics_ids)


@app.route('/place/<int:place_id>', methods=['GET'])
@flask_login.login_required
def place(place_id):
    db_session = get_db_session()
    images = db_session.query(models.Image.id, models.Image.name,
                              models.Image.thumb_width,
                              models.Image.thumb_height,
                              models.Image.width, models.Image.height) \
        .filter(models.Image.place_id == place_id) \
        .order_by(models.Image.creation.desc()).all()

    place_db = db_session.query(models.Place.name) \
        .filter(models.Place.id == place_id).one_or_none()

    if not place_db:
        return flask.abort(404)

    return flask.render_template('library.html', title=place_db.name,
                                 current_user=flask_login.current_user,
                                 images=images)


@app.route('/albums', methods=['GET'])
@flask_login.login_required
def albums():
    db_session = get_db_session()
    albums_list = db_session.query(models.Album.id, models.Album.name).all()
    thumb_pics_ids = {}
    for album_db in albums_list:
        thumb_pics_ids[album_db.id] = db_session.query(models.Image.id) \
            .filter(models.Image.album_id == album_db.id).first().id
    return flask.render_template('albums.html', albums=albums_list,
                                 current_user=flask_login.current_user,
                                 thumb_pics_ids=thumb_pics_ids)


@app.route('/album/<int:album_id>', methods=['GET'])
@flask_login.login_required
def album(album_id):
    db_session = get_db_session()
    images = db_session.query(models.Image.id, models.Image.name,
                              models.Image.thumb_width,
                              models.Image.thumb_height,
                              models.Image.width, models.Image.height) \
        .filter(models.Image.album_id == album_id) \
        .order_by(models.Image.creation.desc()).all()

    album_db = db_session.query(models.Album.name) \
        .filter(models.Album.id == album_id).one_or_none()

    if not album_db:
        return flask.abort(404)

    return flask.render_template('library.html', title=album_db.name,
                                 current_user=flask_login.current_user,
                                 images=images)


@app.route('/thumb/<int:img_id>', methods=['GET'])
@flask_login.login_required
def thumb(img_id):
    db_session = get_db_session()
    img_db = db_session.query(models.Image).filter(models.Image.id == img_id) \
        .one_or_none()

    if not img_db:
        return flask.abort(404)

    bytestream = io.BytesIO(img_db.thumbnail)
    return flask.send_file(bytestream, mimetype="image/jpeg",
                           last_modified=img_db.mtime,
                           cache_timeout=config.cache_max_sec)


@app.route('/image/<int:img_id>', methods=['GET'])
@flask_login.login_required
def image(img_id):
    db_session = get_db_session()
    img_db = db_session.query(models.Image).filter(models.Image.id == img_id) \
        .one_or_none()

    if not img_db:
        return flask.abort(404)

    file = os.path.join(get_project_root(), img_db.path)

    return flask.send_file(file, mimetype="image/jpeg",
                           last_modified=img_db.mtime,
                           cache_timeout=config.cache_max_sec)


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
            return flask.render_template('login.html', form=form,
                                         current_user=flask_login.current_user)

        redir = flask.request.args.get('redir')

        if not web_utils.is_safe_url(redir):
            return flask.abort(400)

        return flask.redirect(redir or flask.url_for('index'))

    return flask.render_template('login.html', form=form,
                                 current_user=flask_login.current_user)


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

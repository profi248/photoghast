import flask
import flask_login
import io
import os

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
        result = db_session.query(models.Image.id) \
            .filter(models.Image.place_id == place_db.id).first()

        if result:
            thumb_pics_ids[place_db.id] = result.id
        else:
            thumb_pics_ids[place_db.id] = 0

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
        result = db_session.query(models.Image.id) \
            .filter(models.Image.album_id == album_db.id).first()
        if result:
            thumb_pics_ids[album_db.id] = result.id
        else:
            thumb_pics_ids[album_db.id] = 0

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

    file = os.path.join(config.image_path, img_db.path)

    return flask.send_file(file, mimetype="image/jpeg",
                           last_modified=img_db.mtime,
                           cache_timeout=config.cache_max_sec)


@app.route('/change-password', methods=['POST'])
@flask_login.login_required
def change_passwd():
    form = forms.ChangePasswordForm()
    if form.validate_on_submit():
        try:
            old_passwd = flask.request.form["old_passwd"]
            new_passwd = flask.request.form["new_passwd"]
            new_passwd_repeat = flask.request.form["new_passwd_repeat"]
        except KeyError:
            return flask.abort(400)

        user_db = user_manager.get_user_db(flask_login.current_user.get_id())
        if not user_manager.check_user_passwd(user_db, old_passwd):
            flask.flash('Old password is incorrect.', 'danger')
            return flask.redirect(flask.url_for('settings'))

        if new_passwd != new_passwd_repeat:
            flask.flash('Passwords do not match.', 'danger')
            return flask.redirect(flask.url_for('settings'))

        if not user_manager.check_password_requirements(new_passwd):
            flask.flash('Changing password failed,'
                        ' minimum password length is 8 characters.', 'danger')
            return flask.redirect(flask.url_for('settings'))

        result = user_manager.change_passwd(user_db, new_passwd)

        if result:
            flask.flash('Password changed successfully.', 'info')
        else:
            flask.flash('Password changing failed.', 'danger')

        return flask.redirect(flask.url_for('settings'))

    for field_name, error_messages in form.errors.items():
        for err in error_messages:
            flask.flash('{}: {}'.format(field_name, err), 'danger')

    flask.redirect(flask.url_for('settings'))


@app.route('/add-user', methods=['POST'])
@flask_login.login_required
def add_user():
    if flask_login.current_user.permissions <= 0:
        return flask.abort(401)

    form = forms.AddUserForm()
    if form.validate_on_submit():
        try:
            username = flask.request.form["username"]
            passwd = flask.request.form["passwd"]
        except KeyError:
            return flask.abort(400)

        try:
            admin_perm = flask.request.form["admin"]
        except KeyError:
            admin_perm = False

        if not user_manager.check_password_requirements(passwd):
            flask.flash('Adding user failed, minimum password length'
                        ' is 8 characters.', 'danger')
            return flask.redirect(flask.url_for('admin'))

        permissions = 1 if admin_perm else 0
        result = user_manager.add_user(username=username, passwd=passwd,
                                       permissions=permissions)

        if result:
            flask.flash('User added successfully.', 'info')
        else:
            flask.flash('Adding user failed, name already taken.', 'danger')

        return flask.redirect(flask.url_for('admin'))

    for field_name, error_messages in form.errors.items():
        for err in error_messages:
            flask.flash('{}: {}'.format(field_name, err), 'danger')

    flask.redirect(flask.url_for('admin'))


@app.route('/admin', methods=['GET'])
@flask_login.login_required
def admin():
    if flask_login.current_user.permissions <= 0:
        return flask.abort(401)

    form = forms.AddUserForm()

    return flask.render_template('admin.html', form=form,
                                 current_user=flask_login.current_user)


@app.route('/settings', methods=['GET'])
@flask_login.login_required
def settings():
    form = forms.ChangePasswordForm()

    return flask.render_template('settings.html', form=form,
                                 current_user=flask_login.current_user)


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
            flask.flash('Username or password is incorrect.', 'warning')
            return flask.render_template('login.html', form=form,
                                         current_user=flask_login.current_user)

        return flask.redirect(flask.url_for('index'))

    for field_name, error_messages in form.errors.items():
        for err in error_messages:
            flask.flash('{}: {}'.format(field_name, err), 'danger')

    return flask.render_template('login.html', form=form,
                                 current_user=flask_login.current_user)


@app.route('/logout', methods=['POST'])
def logout():
    flask_login.logout_user()
    flask.flash('Logged out successfully.', 'info')
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

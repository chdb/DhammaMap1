# coding: utf-8
"""
Provides logic for non-api routes related to user
"""
import flask_login as flog
import flask
import auth
from model.user import MUser
import util
from main import app


@app.route('/user/reset/<token>/', methods=['GET']) # pylint: disable=missing-docstring
def user_reset(token=None):
    """Verifies user's token from url, if it's valid redirects user to page, where he can
    set new password"""
    usr = MUser.get_by('token__', token)
    if not usr:
        flask.flash('Sorry, password reset link is either invalid or expired.')
        return flask.redirect(flask.url_for('index'))

    if auth.is_logged_in():
        flog.logout_user()
        return flask.redirect(flask.request.path)

    # note this is url with '#', so it leads to angular state
    return flask.redirect('%s#!/password/reset/%s' %(flask.url_for('index'), token))


@app.route('/user/verify/<token>/', methods=['GET']) # pylint: disable=missing-docstring
def user_verify(token):
    """Verifies user's email by token provided in url"""
    if auth.is_logged_in():
        flog.logout_user()
        return flask.redirect(flask.request.path)

    usr = MUser.get_by('token__', token)
    if usr and not usr.isVerified_:
        # setting new token is necessary, so this one can't be reused
        usr.token__ = '' # util.randomB64()
        usr.isVerified_ = True
        usr.put()
        auth.logIn(usr)
        flask.flash('Welcome on board %s!' % usr.username)
    else:
        flask.flash('Sorry, activation link is either invalid or expired.')

    return flask.redirect(flask.url_for('index'))

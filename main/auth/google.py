# coding: utf-8
# pylint: disable=missing-docstring, invalid-name

from __future__ import absolute_import

from google.appengine.api import users
import flask

import auth
import model
import util

from main import app


@app.route('/signin/google/')
def signin_google():
    auth.save_request_params()
    google_url = users.create_login_url(flask.url_for('google_authorized'))
    return flask.redirect(google_url)


@app.route('/_s/callback/google/authorized/')
def google_authorized():
    google_user = users.get_current_user()
    if google_user is None:
        flask.flash('You denied the request to sign in.')
        return flask.redirect(flask.url_for('index'))

    usr = retrieve_user_from_google(google_user)
    return auth.signin_via_social(usr)


def retrieve_user_from_google(google_user):
    auth_id = 'federated_%s' % google_user.user_id()
    usr = model.User.get_by('authIDs_', auth_id)
    if usr:
        if not usr.isAdmin_ and users.is_current_user_admin():
            usr.isAdmin_ = True
            usr.put()
        return usr

    return auth.create_or_get_user_db(
        auth_id=auth_id,
        name=util.create_name_from_email(google_user.email()),
        username=google_user.email(),
        email=google_user.email(),
        isVerified_=True,
        isAdmin_=users.is_current_user_admin(),
    )

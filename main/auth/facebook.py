# coding: utf-8
# pylint: disable=missing-docstring, invalid-name

import flask

import auth
import config
from model.user import User
from main import app


facebook_config = dict(
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    base_url='https://graph.facebook.com/',
    # consumer_key=config.CONFIG_DB.auth_facebook_id,
    # consumer_secret=config.CONFIG_DB.auth_facebook_secret,
    request_token_params={'scope': 'email'},
)

facebook = auth.create_oauth_app(facebook_config, 'facebook')


@app.route('/_s/callback/facebook/oauth-authorized/')
def facebook_authorized():
    response = facebook.authorized_response()
    if response is None:
        flask.flash('You denied the request to sign in.')
        return flask.redirect(flask.url_for('index'))

    flask.session['oauth_token'] = (response['access_token'], '')
    me = facebook.get('/me')
    usr = retrieve_user_from_facebook(me.data)
    return auth.signin_via_social(usr)


@facebook.tokengetter
def get_facebook_oauth_token():
    return flask.session.get('oauth_token')


@app.route('/signin/facebook/')
def signin_facebook():
    return auth.signin_oauth(facebook)


def retrieve_user_from_facebook(response):
    auth_id = 'facebook_%s' % response['id']
    usr = User.get_by('authIDs_', auth_id)
    return usr or auth.create_or_get_user_db(
        auth_id=auth_id,
        name=response['name'],
        username=response.get('username', response['name']),
        email_=response.get('email', ''),
        facebook=response.get('id')
    )

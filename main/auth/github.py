# coding: utf-8
# pylint: disable=missing-docstring, invalid-name

import flask
import auth
import config
from main import app
import model.user as user #import User#, UserVdr

github_config = dict(
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    base_url='https://api.github.com/',
    # consumer_key=config.CONFIG_DB.auth_github_id,
    # consumer_secret=config.CONFIG_DB.auth_github_secret,
    request_token_params={'scope': 'user:email'},
)

github = auth.create_oauth_app(github_config, 'github')


@app.route('/_s/callback/github/oauth-authorized/')
def github_authorized():
    response = github.authorized_response()
    if response is None:
        flask.flash('You denied the request to sign in.')
        return flask.redirect(flask.url_for('index'))
    flask.session['oauth_token'] = (response['access_token'], '')
    me = github.get('user')
    usr = retrieve_user_from_github(me.data)
    return auth.signin_via_social(usr)


@github.tokengetter
def get_github_oauth_token():
    return flask.session.get('oauth_token')


@app.route('/signin/github/')
def signin_github():
    return auth.signin_oauth(github)


def retrieve_user_from_github(response):
    auth_id = 'github_%s' % str(response['id'])
    usr = User.get_by('authIDs_', auth_id)
    bio = response['bio'][:user.bio_span[1]] if response['bio'] else ''
    location = response['location'][:user.location_span[1]] if response['location'] else ''
    return usr or auth.create_or_get_user_db(
        auth_id,
        response.get('name', ''),
        response.get('login'),
        response.get('email', ''),
        location=location,
        bio=bio,
        github=response.get('login')
    )

# Todo replace opaque and repeated code such as  
#   bio = response['bio'][:UserVdr.bio_span[1]] if response['bio'] else ''
# with 
#   bio = getField(response, 'bio')
def getField(response, name):
    field = response[name]
    if field:
        span = name + '_span' # depend on validators following this naming convention
        max = getattr(user, span)[1]
        return field [:max]
    return ''

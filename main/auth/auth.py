# coding: utf-8
# pylint: disable=no-self-use
"""
Provides logic for authenticating users
"""
from __future__ import absolute_import
import re
import flask_login as login
from flask_oauthlib import client as oauth
from google.appengine.ext import ndb  # pylint: disable=import-error
import flask
import unidecode
from flask_restful import inputs
from api.helpers   import rqArg, rqParse
from model.user    import User
import task
import util
from security import pwd
import config
import logging

from main import app, config

login_manager = login.LoginManager()  # pylint: disable=invalid-name


class AnonymousUser(login.AnonymousUserMixin):  # pylint: disable=no-init, too-few-public-methods
    """By default, when a user is not actually logged in, current_user is set to
    an AnonymousUserMixin object. It has the following properties and methods:

        is_active and is_authenticated are False
        is_anonymous is True
        get_id() returns None
    """
    usr = None


login_manager.anonymous_user = AnonymousUser


class FlaskUser(AnonymousUser):
    """This provides implementations for the methods that Flask-Login expects user objects to have.
    Flask-Login expects to have these methods:
        get_id
        is_authenticated
        is_active
        is_anonymous
    """

    def __init__(self, usr):
        """Assigns usr to Flask user"""
        self.usr = usr

    def get_id(self):
        """Returns a unicode that uniquely identifies this user, and can be used to load
         the user from the user_loader callback."""
        return self.usr.key.urlsafe()

    def is_authenticated(self):
        """Returns True if the user is authenticated, i.e. they have provided valid credentials"""
        return True

    def is_active(self):
        """Returns True if this is an active user - in addition to being authenticated
       , they also have activated their account, not been suspended"""
        return self.usr.isActive_

    def is_anonymous(self):
        """Returns True if this is an anonymous user. """
        return False


@login_manager.user_loader
def load_user(key):
    """This callback is used to reload the user object from the user ID stored in the session.
    Args    : ndb.Key: Url safe format of ndb.Key of user
    Returns : FlaskUser: if found, returns loaded user as FlaskUser, otherwise None
    """
    usr = ndb.Key(urlsafe=key).get()
    if usr:
        return FlaskUser(usr)
    return None


login_manager.init_app(app)


def current_user_key():
    """Convenient method to get ndb.Key of currently logged user"""
    return login.current_user.usr.key if login.current_user.usr else None


def currentUser():
    """Convenient method to get ndb.Model instance of currently logged user"""
    return login.current_user.usr


def is_logged_in():
    """Convenient method if user is logged in"""
    return bool(login.current_user.usr)


def is_admin():
    """Convenient method if currently logged user is admin"""
    return is_logged_in() and login.current_user.usr.isAdmin_


def is_authorized(user_key):
    """Convenient method for finding out if curretly logged user has given user_key
    or is admin"""
    return current_user_key() == user_key or is_admin()


def create_oauth_app(service_config, name):
    """Creates oauth app for particaular web service

    Args:
        service_config (dict): config required for creating oauth app
        name (string): name of the service, e.g github
    """
    for i in config.CONFIG_DB.authProviders:
        if i.name == name:
            service_config['consumer_key'] = i.id
            service_config['consumer_secret'] = i.secret_
            break
    
    upper_name = name.upper()
    app.config[upper_name] = service_config
    service_oauth = oauth.OAuth()
    service_app = service_oauth.remote_app(name, app_key=upper_name)
    service_oauth.init_app(app)
    return service_app


def save_request_params():
    """Function temporily saves 'remember' url parameter into users session.
    This is useful when we login via oauth, so redirects would wipe out our url parameters."""
    # p = reqparse.RequestParser()
    # p.add_argument('remember', type=inputs.boolean, default=False)
    # args = p.parse_args()
    args = rqParse(rqArg('remember',  type=inputs.boolean, default=False)) 
    flask.session['auth-params'] = { 'remember': args.remember }


def signin_oauth(oauth_app, scheme=None):
    """Attemps to sign in via given oauth_app. If successfull it will redirect to
    appropriate url. EG if signing via github it will call github_authorized as callback function
    Args :  oauth_app(OAuth): Flask Oauth app
            scheme (string) : http or https to use in callback url
    """
    if scheme is None:
        scheme = 'https' if config.PRODUCTION else 'http'
    try:
        flask.session.pop('oauth_token', None)
        save_request_params()
        cb = flask.url_for ( '%s_authorized' % oauth_app.name
                           , _external=True
                           , _scheme=scheme
                           )
        return oauth_app.authorize(callback=cb)
    except oauth.OAuthException:
        logging.exception('oauth exception')
        flask.flash('Something went wrong with sign in. Please try again.')
        return flask.redirect(flask.url_for('index'))


def create_user_db(auth_id, name, username, email='', verified=False, password='', **props):
    """Saves new user into datastore"""
    logging.debug('verified = %r', verified)
    if password:
        password = pwd.encrypt(password)
   # email = email.lower() # todo wrong!
    # Problem: email addresses CAN be case sensitive in local part according to the RFC  
    # Unfortunately some smtp implementations may allow creating distinct addresses which only differ by case. 
    # If someone has created such an mailbox address (whether unwittingly or  unwiselly)
    # he might not recieve quite a lot of mail even if correctly addressed because much sofware ignores the RFC. 
    # But the good mail servers will preserve the case when sending mail.
    # We dont want to be one of the bad ones.
    # Solution:
        # Store emails with case sensitivity
        # Send  emails with case sensitivity
        # Perform all internal searches with case insensitivity
    
    usr = User( name=name
              , email_=email
              , username=username
              , authIDs_=[auth_id] if auth_id else []
              , isVerified_=verified
              , token__=util.randomB64()
              , pwdhash__=password
              , **props
              )
    usr.put()
    if config.CONFIG_DB.notify_on_new_user_:
        task.sendNewUserEmail(usr)
    return usr


def create_or_get_user_db(auth_id, name, username, email='', **kwargs):
    """This function will first lookup if user with given email already exists.
    If so, it will append auth_id for his record and saves it.
    If not we construct a unique username for this user (for the case of signing up via social account)
    and then store it into datastore"""
    usr = User.get_by('email_', email)
    if usr:
        usr.authIDs_.append(auth_id)
        usr.put()
        return usr

    username = normalise_username (username)
    return create_user_db(auth_id, name, username, email_=email, **kwargs)

    
def normalise_username(username):
    ''' # Todo - if its needed at all than rethink this. the logic seems possibly not thought out..
    This might make more sense-
    
    if isinstance(username, unicode):
        username = unidecode.unidecode(username).strip() # convert to ascii, approx transliterating if necessary, and strip whitespace from ends
    username = username.split('@')[0].lower()           # remove everything after and including @, and convert to lower case
    username = re.sub(r'[\W_]+', '.', username)         # replace non-word-chars with dots.  word-char: [a-zA-Z0-9_] 
    '''
    
    if isinstance(username, str):
        username = username.decode('utf-8') # convert to unicode, if necessary      ## but then back to ascii -- why? 
    username = username.split('@')[0].lower() # remove everything after and including @, and convert to lower case
    username = unidecode.unidecode(username).strip() # convert to ascii, approx transliterating if necessary, and strip whitespace from ends
    username = re.sub(r'[\W_]+', '.', username) # replace non-word-chars with dots.  word-char: [a-zA-Z0-9_] 
    
    # make username unique by appending a number suffix - the lowest number necesssary.
    new_username = username
    suffix = 1
    while not User.is_username_available(new_username):
        new_username = '%s%d' % (username, suffix)
        suffix += 1
    return new_username

    
def signin_user_db(usr, remember=False):
    """Signs in given user"""
    flask_user_db = FlaskUser(usr)
    auth_params = flask.session.get ('auth-params'
                                    , { 'remember': remember
                                    } )
    flask.session.pop('auth-params', None)
    return login.login_user(flask_user_db, remember=auth_params['remember'])


def signout_user():
    """Signs out given user"""
    login.logout_user()


def signin_via_social(*args, **kwargs):
    """Signs in given, when he used social account and then it redirects him to home page"""
    if not signin_user_db(*args, **kwargs):
        flask.flash('Sorry, there was an error while signing you in')
    return flask.redirect(flask.url_for('index'))

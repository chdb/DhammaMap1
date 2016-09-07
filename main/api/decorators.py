"""
Provides decorator functions for api methods, which are used as middleware for processing requests
"""

import functools
from google.appengine.ext import ndb #pylint: disable=import-error
from flask import g, abort
from helpers import ArgVdr, rqArg, rqParse
from main import config, auth
from flask_restful import inputs
import model
from werkzeug import exceptions
import logging

def model_by_key(func):
    """This decorator gets model by ndb.Key, which is passed in URL
    Raises  : HTTPException    : if key was not found in data store
    """
    @functools.wraps(func)
    def decorated_function(*args, **kwargs): # pylint: disable=missing-docstring
        g.model_key = ndb.Key(urlsafe=kwargs['key'])
        logging.debug('xxxxxxxxxxxxxxxxxxx key = %r' , g.model_key)
        g.model_db = g.model_key.get()
        if g.model_db:
            return func(*args, **kwargs)
        raise exceptions.NotFound() #return make_not_found_exception()

    return decorated_function


def verify_captcha(form_name):
    """This decorator performs captcha validation. 'form_name' is to used to determine if captcha is enabled/disabled in CONFIG_DB.
    We can turn off specific form with captcha in Admin - useful when developing.
    Args    : form_name (string): captcha for this form is enabled iff form_name is saved in CONFIG_DB.recaptcha_forms
    Raises  : ValueError        : if captcha is invalid.
    """
    def decorator(func):  # pylint: disable=missing-docstring
        @functools.wraps(func)
        def decorated_function(*args, **kwargs):  # pylint: disable=missing-docstring
            if form_name in config.CONFIG_DB.recaptcha_forms:
                # p = reqparse.RequestParser()
                # p.add_argument('captcha', type=ArgVdr.fn('captcha'), required=True)
                # p.parse_args()
                rqParse(rqArg('email', argVdr='captcha'), required=True) 
            return func(*args, **kwargs)

        return decorated_function

    return decorator


def user_by_username(func):
    """Gets User model by username in URL and assigns it into g.usr"""
    @functools.wraps(func)
    def decorated_function(*args, **kwargs): # pylint: disable=missing-docstring
        g.usr = model.User.get_by('username', kwargs['username'])
        if g.usr:
            return func(*args, **kwargs)
        raise exceptions.NotFound() #return make_not_found_exception()

    return decorated_function


def login_required(func):
    """Returns 401 error if user is not logged-in when requesting the given API URL"""
    @functools.wraps(func)
    def decorated_function(*args, **kwargs): # pylint: disable=missing-docstring
        if auth.is_logged_in():
            return func(*args, **kwargs)
        return abort(401)

    return decorated_function


def admin_required(func):
    """Returns 401 response if user is not logged-in when requesting the given API URL
    or returns 403 response if user is not admin     when requesting the given API URL
    """
    @functools.wraps(func)
    def decorated_function(*args, **kwargs): # pylint: disable=missing-docstring
        if auth.is_admin():
            return func(*args, **kwargs)
        if not auth.is_logged_in():
            return abort(401)
        return abort(403)

    return decorated_function


def authorization_required(func):
    """Returns 401 response if user is not logged-in when requesting URL with user ndb.Key in it
    or Returns 403 response if logged-in user's ndb.Key is different from ndb.Key given in requested URL.
    """
    @functools.wraps(func)
    def decorated_function(*args, **kwargs): # pylint: disable=missing-docstring
        if auth.is_authorized(ndb.Key(urlsafe=kwargs['key'])):
            return func(*args, **kwargs)
        if not auth.is_logged_in():
            return abort(401)
        return abort(403)

    return decorated_function


def parse_signin(func):
    """Parses credentials posted by client and loads appropriate user from datastore"""
    @functools.wraps(func)
    def decorated_function(*args, **kwargs): # pylint: disable=missing-docstring
        # p = reqparse.RequestParser()
        # p.add_argument('login', type=str, required=True)
        # p.add_argument('password', type=model.UserVdr.fn('password_span'), required=True)
        # p.add_argument('remember', type=inputs.boolean, default=False)
        # g.args = p.parse_args()
        
        g.args = rqParse( rqArg('login'   , type=str                , required=True)
                        , rqArg('password', userVdr='password_span', required=True)
                        , rqArg('remember', type=inputs.boolean     , default=False)
                        ) 
        
        g.usr = model.User.get_by_credentials(g.args.login, g.args.password)
        return func(*args, **kwargs)

    return decorated_function

"""
Provides decorator functions for api methods, which are used as middleware for processing requests
"""

import functools
from google.appengine.ext import ndb #pylint: disable=import-error
# from flask import g, abort
#from helpers import rqParse
# from main import auth
# from flask_restful import inputs
import model.user as user 
#from werkzeug import exceptions
import validators as vdr
import logging
from model.config import CONFIG_DB
from webapp2 import abort


def verify_captcha(form_name):
    """This decorator performs captcha validation. 'form_name' is to used to determine if captcha is enabled/disabled in CONFIG_DB.
    We can turn off specific form with captcha in Admin - useful when developing.
    Args    : form_name (string): captcha for this form is enabled iff form_name is in CONFIG_DB.recaptcha_forms
    Raises  : ValueError        : if captcha is invalid.
    """
    def decorator(func):  # pylint: disable=missing-docstring
        @functools.wraps(func)
        def decFunc(handler, *pa, **ka):  # pylint: disable=missing-docstring
            if form_name in CONFIG_DB.recaptcha_forms:
                handler.args = _s.parseJson(('captcha', vdr.captchaVdr))
            return func(handler, *pa, **ka)
        return decFunc
    return decorator

    
def entByKey(func):
    """This decorator gets model by ndb.Key, which is passed in URL
    Raises  : HTTPException    : if key was not found in data store
    """
    @functools.wraps(func)
    def decorator(*pa, **ka): # pylint: disable=missing-docstring
        g.ndbKey = ndb.Key (urlsafe=ka['key'])
        #logging.debug('xxxxxxxxxxxxxxxxxxx entByKey: key = %r' , g.ndbKey)
        g.ndbEnt = g.ndbKey.get()
        if g.ndbEnt:
            return func(*pa, **ka)
        raise exceptions.NotFound() #return make_not_found_exception()
    return decorator
    

def usrByUsername(func):
    """Gets User model by username in URL and assigns it into g.usr"""
    @functools.wraps(func)
    def decorator(*pa, **ka): # pylint: disable=missing-docstring
        g.usr = user.byUsername(ka['username'])
        if g.usr:
            return func(*pa, **ka)
        raise exceptions.NotFound() #return make_not_found_exception()
    return decorator


# def usrByCredentials (func):
    # """Parses credentials posted by client and loads appropriate user from datastore"""
    # @functools.wraps(func)
    # def decorator(handler, *pa, **ka): # pylint: disable=missing-docstring
        # logging.debug('uriData: %r', handler.request.uriData)
        # logging.debug('formData: %r', handler.request.formData)

        
        # g.args = rqParse(handler.request.uriData
                        # , ('loginId'              )
                        # , ('password', vdr.password_span)
                        # , ('remember', vdr.toBool, False)
                        # ) 
        # g.usr = user.byCredentials(g.args.loginId, g.args.password)
        # return func(handler, *pa, **ka)

    # return decorator

    
def login_required(func):
    """Returns 401 error if user is not logged-in when requesting the given API URL"""
    @functools.wraps(func)
    def decorator(handler, *pa, **ka): # pylint: disable=missing-docstring
        if auth.is_logged_in():
            return func(*pa, **ka)
        return abort(401)
    return decorator


def admin_required(func):
    """Returns 401 response if user is not logged-in when requesting the given API URL
    or returns 403 response if user is not admin     when requesting the given API URL
    """
    @functools.wraps(func)
    def decorator(*pa, **ka): # pylint: disable=missing-docstring
        if auth.is_admin():
            return func(*pa, **ka)
        if not auth.is_logged_in():
            return abort(401)
        return abort(403)
    return decorator


def authorization_required(func):
    """Returns 401 response if user is not logged-in when requesting URL with user ndb.Key in it
    or Returns 403 response if logged-in user's ndb.Key is different from ndb.Key given in requested URL.
    """
    @functools.wraps(func)
    def decorator(*pa, **ka): # pylint: disable=missing-docstring
        if auth.is_authorized(ndb.Key(urlsafe=ka['key'])):
            return func(*pa, **ka)
        if not auth.is_logged_in():
            return abort(401)
        return abort(403)
    return decorator


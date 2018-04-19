"""
Provides decorator functions for api methods, which are used as middleware for processing requests
"""

import logging
import functools
from webapp2 import abort
#from google.appengine.ext import ndb #pylint: disable=import-error
# from flask import g, abort
#from helpers import rqParse
# from main import auth
# from flask_restful import inputs
import model.mUser as mUser
#from werkzeug import exceptions
import validators as vdr
#from config import appCfg
from app import app


def verify_captcha(form_name):
    """This decorator performs captcha validation. 'form_name' is to used to determine if captcha is enabled/disabled in CONFIG_DB.
    We can turn off specific form with captcha in Admin - useful when developing.
    Args    : form_name(string): captcha for this form is enabled iff form_name is in CONFIG_DB.recaptcha_forms
    Raises  : ValueError        : if captcha is invalid.
    """
    def decorator(fn):  # pylint: disable=missing-docstring
        @functools.wraps(fn)
        def decFn(hlr, *pa, **ka):  # pylint: disable=missing-docstring
            logging.debug('verify_captcha ****************************************************************************************')
            if app.cfg.has_recaptcha(form_name):
                hlr.args = hlr.parseJson(('captcha', vdr.captchaVdr), ipa=hlr.request.remote_addr)
            return fn(hlr, *pa, **ka)
        return decFn
    return decorator


# def entByKey(func):
#     """This decorator gets model by ndb.Key, which is passed in URL
#     Raises  : HTTPException    : if key was not found in data store
#     """
#     @functools.wraps(func)
#     def decorator(*pa, **ka): # pylint: disable=missing-docstring
#         g.ndbKey = ndb.Key(urlsafe=ka['key'])
#         #logging.debug('xxxxxxxxxxxxxxxxxxx entByKey: key = %r' , g.ndbKey)
#         g.ndbEnt = g.ndbKey.get()
#         if g.ndbEnt:
#             return func(*pa, **ka)
#         raise exceptions.NotFound() #return make_not_found_exception()
#     return decorator


# def usrByUsername(func):
    # """Gets User model by username in URL and assigns it into g.usr"""
    # @functools.wraps(func)
    # def decorator(*pa, **ka): # pylint: disable=missing-docstring
        # g.usr =mUser.byUsername(ka['username'])
        # if g.usr:
            # return func(*pa, **ka)
        # raise exceptions.NotFound() #return make_not_found_exception()
    # return decorator


# def usrByCredentials(func):
    # """Parses credentials posted by client and loads appropriate user from datastore"""
    # @functools.wraps(func)
    # def decorator(handler, *pa, **ka): # pylint: disable=missing-docstring
        # logging.debug('uriData: %r', handler.request.uriData)
        # logging.debug('formData: %r', handler.request.formData)


        # g.args = rqParse(handler.request.uriData
                        # ,('loginId'              )
                        # ,('password', vdr.password_span)
                        # ,('remember', vdr.toBool, False)
                        # )
        # g.usr = user.byCredentials(g.args.loginId, g.args.password)
        # return func(handler, *pa, **ka)

    # return decorator


def login_required(func):
    """Returns 401 error if user is not logged-in"""
    @functools.wraps(func)
    def decorator(handler, *pa, **ka): # pylint: disable=missing-docstring
        if handler.ssn.isLoggedIn():
            return func(handler, *pa, **ka)
        return abort(401)
    return decorator

#
def adminOnly(func):
    """returns 403 response if user is not admin"""
    @functools.wraps(func)
    @login_required
    def decorator(handler, *pa, **ka): # pylint: disable=missing-docstring

        #if auth.is_admin():

         # usr = u.MUser.get_by_id(_s.ssn['_userID'])
        liu = handler.loggedInUser
        if liu and liu.isAdmin_:
            return func(handler, *pa, **ka)
        # if not auth.is_logged_in():
            # return abort(401)
        return abort(403)
    return decorator


def authorization_required(func):
    """Returns 401 response if user is not logged-in when requesting URL with user id in it
    or Returns 403 response if logged-in user's id is different from id given in requested URL.
    """
    @functools.wraps(func)
    def decorator(handler, *pa, **ka): # pylint: disable=missing-docstring
        #logging.debug('ka: %r', ka)
        #logging.debug('pa: %r', pa)
        if handler.ssn.isLoggedIn():
            liuid = handler.ssn['_userID'] #loggedInUserId
            liu = mUser.MUser.get_by_id(liuid) #loggedInUser
            #ka['usr'] = usr
            if liu.isAdmin_ or liuid == ka['uid']:
                return func(handler, *pa, **ka)
            return abort(403)
        return abort(401)
    return decorator

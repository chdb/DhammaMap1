# coding: utf-8
# pylint: disable=too-few-public-methods, missing-docstring, unused-argument
"""
Provides API logic relevant to user authentication
"""
#from flask_restful import inputs, Resource
#from flask import g, abort

import logging
try:  import simplejson as json
except ImportError: import json

from google.appengine.ext import ndb  # pylint: disable=import-error

import task
import util
# import auth
from config import appCfg
from model import mUser as u
#from main import API
#from werkzeug import exceptions as exc
# import control.error as exc
import validators as v
from security import pwd
#from handlers.api.helpers import ok #, rqParse
from handlers.api.decorators import verify_captcha #, usrByCredentials
from handlers.api.throttle import RateLimiter,credentials
from handlers.basehandler import HAjax
from app import app
from signup_q import Midstore
#from session import Cookie
#from webob.exc import HTTPUnprocessableEntity

@app.API_1('auth/unique_ema')
class HEmailVdr(HAjax):
    def post(_s):
        # todo: Security - dont provide user info on validated uniqueness here - send this info in email response
        _s.parseJson(('email_', u.emailUniqueVdr )) # todo instead change this to check ema format with MailGun Validator

@app.API_1('auth/signup')
class HSignup(HAjax):
    @verify_captcha('signupForm')
    def post(_s):
        """Create new user account"""
        args = _s.parseJson(('email_'   , u.emailUniqueVdr  ) #todo
                           ,('name'     ,)
                           ,('password' , v.password_span   )
                           ,('repeatPwd', v.password_span   )
                            #  ,('remember', v.toBool,    False)
                           )
        #todo   remove password to HVerify
        #       save data in pullQ

        # usr = u.MUser.create( username   =args.username
                           # , email_     =args.email_
                           # , isVerified_=not appCfg.verify_email
                           # , pwdhash__  =pwd.encrypt(args.password)
                           # )
        if appCfg.notify_on_new_user_:
            task.sendNewUserEmail(args)

        nonce = util.randomB64(appCfg.NonceBYTES)
        tag = Midstore('SignupQ').put(nonce, args.email_, args.name)
        task.sendVerifyEmail(args.email_, nonce, tag)
        #_s.flash('OK - an email has been sent')
        # else: # if users don't need to verify email, we sign in new user
            # _s.logIn(usr, remember=args.remember)
            # return usr.toDict()


@app.API_1('auth/verify/<token>') # pylint: disable=missing-docstring
class HVerify(HAjax):
    def get(_s, token):
        """Verifies user's email by token provided in url"""
        logging.debug('NNNNNNNNNNNNNNNNNNN token = %r', token)
        if _s.ssn.logOut():
            _s.redirect(_s.request.path)

        data = Midstore('SignupQ').get(token)
 #       verifyCookie = Cookie('vdata', httponly=False)
     #   cookie.set(_s, data)
        # usr = MUser.get_by('token__', token)
        # if usr and not usr.isVerified_:
            # setting new token is necessary, so this one can't be reused
            #usr.token__ = '' # util.randomB64()
            #usr.isVerified_ = True
        #_s.redirect_to('signup2')
        # note this is url with '#', so it leads to angular state
        #_s.redirect('%s#!/password/reset/%s' %(_s.url_for('home'), token))
        logging.debug('NNNNNNNNNNNNNNNNNNN data = %r', data)
        logging.debug('NNNNNNNNNNNNNNNNNNN uri = %r', '%s#!/signup2/%s' %(_s.url_for('home'), token))

        # _s.redirect('%s#!/signup2/%s' %(_s.url_for('home'), token))
        return data

        # if data:
            # logging.debug('NNNNNNNNNNNNNNNNNNNN data = %r', data)
            # usr = u.MUser.create(data)
            # _s.logIn(usr)
            # _s.flash('Welcome on board %s!' % usr.username)
        # else:
            # _s.flash('Sorry, activation link is either invalid or expired.')

        # _s.redirect_to('home')

@app.API_1('auth/signup2')
class HSignup2(HAjax):
    def post(_s):
        """Create new user account"""
        args = _s.parseJson(('email_'  , u.emailUniqueVdr  )
                        #   ,('username', u.usrnameUniqueVdr)
                           ,('password', v.password_span   )
                           ,('remember', v.toBool,    False)
                           ,('token'   , v.token_span      )
                           )
        token = util.utf8(args.pop('token'))
        data = Midstore('SignupQ').pop(token)
        if data:
            data2 = json.loads(data)
            if data2['email_'] == args.email_:
 #          (and data2['username'] == args.username):
                rmbr = args.pop('remember')
                usr = u.MUser.create(**args)
                _s.logIn(usr, rmbr)
                return usr.toDict()

            logging.warning('wrong data')
        else:
            logging.warning('no data ')
        # else:
        # return
        # usr = u.MUser.create( username   =args.username
                            # , email_     =args.email
                           # , isVerified_=not appCfg.verify_email
                           # , pwdhash__  =pwd.encrypt(args.password)
                           # )
        # if appCfg.notify_on_new_user_:
         #   task.sendNewUserEmail(args)

        #if appCfg.verify_email:
        #task.sendVerifyEmail(args)
        #_s.flash('OK - an email has been sent')
        # else: # if users don't need to verify email, we sign in new user
            # _s.logIn(usr, remember=args.remember)

#@verify_captcha('signinForm')
@app.API_1('auth/logIn')
class HLogIn(HAjax):

    @credentials
    #@verify_captcha('signinForm')
    #@rateLimit #todo implement rateLimit calling code in other handlers(HForgotPassword HVerify)
    def post(_s, loginId, password, remember):
        """Signs in existing user."""
        resp = {}
        rl = RateLimiter(loginId, _s)
        if not rl.ready():
            resp['delay']= rl.delay
        else:
            usr = u.MUser.byCredentials(loginId, password)
            rl.tryLock(bool(usr))
            if usr:
 #               if usr.isActive_:
                _s.logIn(usr, remember=remember)
                resp['user']= usr.toDict()
                if usr.isAdmin_:
                    resp['adminCfg']= appCfg.toDict(nullVals=True)
            else:
                taskdata = Midstore('SignupQ').findEma(loginId)
                if taskdata:
                    resp['unVerified']= taskdata
                else:
                    _s.abort(401,'These credentials are invalid')
        return resp


@app.API_1('auth/logOut')
class HLogOut(HAjax):
    def post(_s):
        _s.logOut()


@app.API_1('auth/resendSignup')
class HResendSignUp(HAjax):
   # @usrByCredentials
   # @credentials
    def post(_s): #, loginId, password, remember
        """Resend the verification email to user"""

        args = _s.parseJson(('ema' , v.loginId_span)
                           ,('name', v.name_span)
                        #   ,('remember', v.toBool, False)
                           ,('nonce', )
                           ,('tag'  , )
                           )
        # usr = u.byCredentials(loginId, password)
        # if usr:
            # if not usr.isActive_:
                # abort(423)
                # raise exc.Locked('your account is locked until...') # todo "... until when"
            #if not usr.isVerified_:
        if '@' in args.ema:
            task.sendVerifyEmail(args.ema, args.nonce, args.tag)
        else: logging.warning('loginId is a username not email address')


@app.API_1('auth/forgotPassword')
class HForgotPassword(HAjax):
    def post(_s):
        """Send email with reset-password token, to user"""
        args = _s.parseJson(('email_',))
        usr = u.MUser.byEmail(args.email_)
        if usr:
            task.sendResetEmail(usr)
        else: logging.warning('ema not found : %r', args.email_)


@app.API_1('auth/resetPassword')
class HResetPassword(HAjax):
    @ndb.toplevel #so we can perform asynchronous put and sign-in in parallel
    def post(_s):
        """Sets new password given by user if he provides valid token
        """
        args = _s.parseJson(('token'      , v.token_span)
                           ,('newPassword', v.password_span)
                           )
        usr = u.MUser.get_by('token__', args.token) # todo encode uid with token, or put token in AuthId, so we can replace get_by
        usr.pwdhash__ = pwd.encrypt(args.newPassword)
        usr.token__ = util.randomB64()
  #      usr.isVerified_ = True
        usr.put_async()
        _s.logIn(usr)
        return usr.toDict()

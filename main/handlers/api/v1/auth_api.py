# coding: utf-8
# pylint: disable=too-few-public-methods, no-_s-use, missing-docstring, unused-argument
"""
Provides API logic relevant to user authentication
"""
#from flask_restful import inputs, Resource
#from flask import g, abort

import util
# import auth
from model.config import CONFIG_DB
from model import user as u
import task
#from main import API
from google.appengine.ext import ndb  # pylint: disable=import-error
#from werkzeug import exceptions as exc
# import control.error as exc
import validators as v
from security import pwd
from handlers.api.helpers import ok #, rqParse
from handlers.api.decorators import verify_captcha #, usrByCredentials
from handlers.api.throttle import rateLimit
import logging


from handlers.basehandler import HBase
#@API.resource('/api/v1/auth/signup')
#class SignupAPI(Resource):
class HSignUp(HBase):

    @verify_captcha('signupForm')
    def post(_s):
        """Create new user account"""
              
        args = _s.parseJson(('email'   , u.emailUniqueVdr  )
                           ,('username', u.usrnameUniqueVdr)
                           ,('password', v.password_span   )
                           ,('remember', v.toBool,    False)
                           )
        usr = u.User.create( username   =args.username
                           , email_     =args.email
                           , isVerified_=not CONFIG_DB.verify_email
                           , pwdhash__  =pwd.encrypt(args.password)
                           )
        if CONFIG_DB.notify_on_new_user_:
            task.sendNewUserEmail(usr)

        if CONFIG_DB.verify_email:
            task.sendVerifyEmail(usr)
            return ok()
        # if users don't need to verify email, we automaticaly signin newly registered user
        auth.signIn(usr, remember=args.remember)
        return usr.toDict(publicOnly=False)


#@API.resource('/api/v1/auth/signin')
class SigninAPI(HBase):
    @verify_captcha('signinForm')
 #   @rateLimit
    def post(_s):
        """Signs in existing user."""
        #return {'delay': 2000}
        usr, rmbr = _s.usrByCredentials()
        if usr is None:
            return None
        
        if  usr.isVerified_ \
        and usr.isActive_ :
            _s.signIn(usr, remember=rmbr)
        return _s.ajaxResponse(user=usr.toDict(publicOnly=False))


#@API.resource('/api/v1/auth/signout')
class SignoutAPI(HBase):
    def post(_s):
        """Signs out user. Also it sends back a public config object to update client in case
        previous user was admin and so client config object included private data"""
        auth.signOut()
        app_config = CONFIG_DB.toDict()
        return app_config


#@API.resource('/api/v1/auth/resend-verification')
class ResendActivationAPI(HBase):
   # @usrByCredentials
    def post(_s):
        """Resends email verification to user"""
        if g.usr: 
            if not g.usr.isActive_:
                # abort(423)
                raise exc.Locked('your account is locked until...') # todo "... until when"
            if not g.usr.isVerified_:
                task.sendVerifyEmail(g.usr)
        return ok()


#@API.resource('/api/v1/auth/forgot')
class ForgotPasswordAPI(HBase):
    def post(_s):
        """Sends email with token for resetting password to an user"""
        args = _s.parseJson(('email', u.emailExistsVdr))       
        usr = u.byEmail(args.email)
        assert usr
        task.sendResetEmail(usr)
        return ok()

            
#@API.resource('/api/v1/auth/reset')
class ResetPasswordAPI(HBase):
    @ndb.toplevel
    def post(_s):
        """Sets new password given by user if he provided valid token
        Notice ndb.toplevel decorator here, so we can perform asynchronous put and sign-in in parallel
        """
        args = _s.parseJson(('token'      , v.token_span)
                           ,('newPassword', v.password_span)
                           )
        usr = u.User.get_by('token__', args.token) # todo encode uid with token, or put token in AuthId, so we can replace get_by
        usr.pwdhash__ = pwd.encrypt(args.newPassword)
        usr.token__ = util.randomB64()              
        usr.isVerified_ = True
        usr.put_async()
        auth.signIn(usr)
        return usr.toDict(publicOnly=False)

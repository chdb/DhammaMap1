# coding: utf-8
# pylint: disable=too-few-public-methods, no-self-use, missing-docstring, unused-argument
"""
Provides API logic relevant to user authentication
"""
from flask_restful import inputs, Resource
from flask import g, abort
import util
import auth
import config
from model import user as u
import task
from main import API
from api.helpers import ok, rqArg, rqParse, Handler
from api.decorators import verify_captcha, usrByCredentials
from google.appengine.ext import ndb  # pylint: disable=import-error
#from werkzeug import exceptions as exc
import control.error as exc
import validators as v
from security import pwd
from api.throttle import rateLimit
import logging


@API.resource('/api/v1/auth/signup')
class SignupAPI(Resource):
    @verify_captcha('signupForm')
    def post(self):
        """Creates new user account, given valid arguments"""
        args = rqParse( rqArg('email'   ,vdr=u.emailUniqueVdr, required=True)
                      , rqArg('username',vdr=u.usrnameUniqueVdr)
                      , rqArg('password',vdr=v.password_span)
                      , rqArg('remember',type=inputs.boolean, default=False)
                      )
        usr = u.User.create( username=args.username
                           , email_=args.email
                           , isVerified_= not config.CONFIG_DB.verify_email
                           , pwdhash__=pwd.encrypt(args.password)
                           )
        if config.CONFIG_DB.notify_on_new_user_:
            task.sendNewUserEmail(usr)

        if config.CONFIG_DB.verify_email:
            task.sendVerifyEmail(usr)
            return ok()
        # if users don't need to verify email, we automaticaly signin newly registered user
        auth.signIn(usr, remember=args.remember)
        return usr.toDict(publicOnly=False)


@API.resource('/api/v1/auth/signin')
class SigninAPI(Handler):
    @verify_captcha('signinForm')
    @usrByCredentials #sets g.usr 
    @rateLimit
    def post(self):
        """Signs in existing user."""
        #return {'delay': 2000}
        
        if g.usr is None:
            return None
        
        if  g.usr.isVerified_ \
        and g.usr.isActive_ :
            auth.signIn(g.usr, remember=g.args.remember)
        return {'user': g.usr.toDict(publicOnly=False)}


@API.resource('/api/v1/auth/signout')
class SignoutAPI(Resource):
    def post(self):
        """Signs out user. Also it sends back a public config object to update client in case
        previous user was admin and so client config object included private data"""
        auth.signOut()
        app_config = config.CONFIG_DB.toDict()
        return app_config


@API.resource('/api/v1/auth/resend-verification')
class ResendActivationAPI(Resource):
    @usrByCredentials
    def post(self):
        """Resends email verification to user"""
        if g.usr: 
            if not g.usr.isActive_:
                # abort(423)
                raise exc.Locked('your account is locked until...') # todo "... until when"
            if not g.usr.isVerified_:
                task.sendVerifyEmail(g.usr)
        return ok()


@API.resource('/api/v1/auth/forgot')
class ForgotPasswordAPI(Resource):
    def post(self):
        """Sends email with token for resetting password to an user"""
        args = rqParse( rqArg('email', vdr=u.emailExistsVdr))       
        usr = u.byEmail(args.email)
        assert usr
        task.sendResetEmail(usr)
        return ok()

            
@API.resource('/api/v1/auth/reset')
class ResetPasswordAPI(Resource):
    @ndb.toplevel
    def post(self):
        """Sets new password given by user if he provided valid token
        Notice ndb.toplevel decorator here, so we can perform asynchronous put and sign-in in parallel
        """
        args = rqParse( rqArg('token'      , vdr=v.token_span)
                      , rqArg('newPassword', vdr=v.password_span, dest='new_password')
                      )
        usr = u.User.get_by('token__', args.token) # todo encode uid with token, or put token in AuthId, so we can replace get_by
        usr.pwdhash__ = pwd.encrypt(args.new_password)
        usr.token__ = util.randomB64()              
        usr.isVerified_ = True
        usr.put_async()
        auth.signIn(usr)
        return usr.toDict(publicOnly=False)

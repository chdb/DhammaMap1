# coding: utf-8
# pylint: disable=too-few-public-methods, no-self-use, missing-docstring, unused-argument
"""
Provides API logic relevant to user authentication
"""
from flask_restful import inputs, Resource
from flask import g
import util
import auth
import config
from model.user import User#, UserVdr, Config
import task
from main import API
from api.helpers import ok, rqArg, rqParse
from api.decorators import verify_captcha, parse_signin
from google.appengine.ext import ndb  # pylint: disable=import-error
from werkzeug import exceptions
import validators as vdr
from security import pwd
import logging

@API.resource('/api/v1/auth/signup')
class SignupAPI(Resource):
    @verify_captcha('signupForm')
    def post(self):
        """Creates new user account, given valid arguments"""
        args = rqParse( rqArg('email'   ,vdr=User.emailUniqueVdr, required=True)
                      , rqArg('username',vdr=User.usrnameUniqueVdr)
                      , rqArg('password',vdr=vdr.password_span)
                      , rqArg('remember',type=inputs.boolean, default=False)
                      )
        usr = auth.create_user_db  ( auth_id=None
                                   , name=''
                                   , username=args.username
                                   , email=args.email
                                   , verified= not config.CONFIG_DB.verify_email
                                   , password=args.password
                                   )
        usr.put()
        if config.CONFIG_DB.verify_email:
            task.sendVerifyEmail(usr)
            return ok()
        # if users don't need to verify email, we automaticaly signin newly registered user
        auth.signin_user_db(usr, remember=args.remember)
        return usr.toDict(publicOnly=False)


@API.resource('/api/v1/auth/signin')
class SigninAPI(Resource):
    @verify_captcha('signinForm')
    @parse_signin
    def post(self):
        """Signs in existing user. Note, g.usr is set by parse_signin decorator"""
        if g.usr and g.usr.isVerified_ and g.usr.isActive_:
            auth.signin_user_db(g.usr, remember=g.args.remember)

        if g.usr is None:
            raise exceptions.BadRequest('Seems like these credentials are invalid')

        return g.usr.toDict(publicOnly=False)


@API.resource('/api/v1/auth/signout')
class SignoutAPI(Resource):
    def post(self):
        """Signs out user. Also it sends back a public config object to update client in case
        previous user was admin and so client config object included private data"""
        auth.signout_user()
        app_config = config.CONFIG_DB.toDict()
        return app_config


@API.resource('/api/v1/auth/resend-verification')
class ResendActivationAPI(Resource):
    @parse_signin
    def post(self):
        """Resends email verification to user"""
        if g.usr and not g.usr.isVerified_ and g.usr.isActive_:
            task.sendVerifyEmail(g.usr)
        return ok()


@API.resource('/api/v1/auth/forgot')
class ForgotPasswordAPI(Resource):
    def post(self):
        """Sends email with token for resetting password to an user"""
        args = rqParse( rqArg('email', vdr=User.emailExistsVdr))       
        usr = User.get_by('email_', args.email)
        task.sendResetEmail(usr)
        return ok()


@API.resource('/api/v1/auth/reset')
class ResetPasswordAPI(Resource):
    @ndb.toplevel
    def post(self):
        """Sets new password given by user if he provided valid token
        Notice ndb.toplevel decorator here, so we can perform asynchronous put and sign-in in parallel
        """
        args = rqParse( rqArg('token'      , vdr=vdr.token_span)
                      , rqArg('newPassword', vdr=vdr.password_span, dest='new_password')
                      )
        usr = User.get_by('token__', args.token)
        usr.pwdhash__ = pwd.encrypt(args.new_password)
        usr.token__ = util.randomB64()
        usr.isVerified_ = True
        usr.put_async()
        auth.signin_user_db(usr)
        return usr.toDict(publicOnly=False)

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
from model import User, UserVdr, Config
import task
from main import API
from api.helpers import empty_ok_response, rqArg, rqParse
from api.decorators import verify_captcha, parse_signin
from google.appengine.ext import ndb  # pylint: disable=import-error
from werkzeug import exceptions
import logging

@API.resource('/api/v1/auth/signup')
class SignupAPI(Resource):
    @verify_captcha('signupForm')
    def post(self):
        """Creates new user account if provided valid arguments"""
        # p = reqparse.RequestParser()
        # p.add_argument('email'   , type=UserVdr.fn('unique_email'), required=True)
        # p.add_argument('username', type=UserVdr.fn('unique_username'))
        # p.add_argument('password', type=UserVdr.fn('password_span'))
        # p.add_argument('remember', type=inputs.boolean, default=False)
        # args = p.parse_args()

        # logging.debug('args1 = %r', args)
        
        args = rqParse( rqArg('email'   , userVdr='unique_email', required=True)
                      , rqArg('username', userVdr='unique_username')
                      , rqArg('password', userVdr='password_span')
                      , rqArg('remember', type=inputs.boolean, default=False)
                      )

        logging.debug('args2 = %r', args)
        
        user_db = auth.create_user_db  ( auth_id=None
                                       , name=''
                                       , username=args.username
                                       , email=args.email
                                       , verified= not config.CONFIG_DB.verify_email
                                       , password=args.password
                                       )
        user_db.put()

        if config.CONFIG_DB.verify_email:
            task.sendVerifyEmail(user_db)
            return empty_ok_response()

        # if users don't need to verify email, we automaticaly signin newly registered user
        auth.signin_user_db(user_db, remember=args.remember)
        return user_db.to_dict(all=True)


@API.resource('/api/v1/auth/signin')
class SigninAPI(Resource):
    @verify_captcha('signinForm')
    @parse_signin
    def post(self):
        """Signs in existing user. Note, g.user_db is set by parse_signin decorator"""
        if g.user_db and g.user_db.verified_p and g.user_db.active_p:
            auth.signin_user_db(g.user_db, remember=g.args.remember)

        if g.user_db is None:
            raise exceptions.BadRequest('Seems like these credentials are invalid')

        return g.user_db.to_dict(all=True)


@API.resource('/api/v1/auth/signout')
class SignoutAPI(Resource):
    def post(self):
        """Signs out user. Also it sends back a public config object to update client in case
        previous user was admin and so client config object included private data"""
        auth.signout_user()
        app_config = config.CONFIG_DB.to_dict()
        return app_config


@API.resource('/api/v1/auth/resend-verification')
class ResendActivationAPI(Resource):
    @parse_signin
    def post(self):
        """Resends email verification to user"""
        if g.user_db and not g.user_db.verified_p and g.user_db.active_p:
            task.sendVerifyEmail(g.user_db)
        return empty_ok_response()


@API.resource('/api/v1/auth/forgot')
class ForgotPasswordAPI(Resource):
    def post(self):
        """Sends email with token for resetting password to an user"""
        args = rqParse( rqArg('email', userVdr='existing_email'))       
        user_db = User.get_by('email_p', args.email)
        task.sendResetEmail(user_db)
        return empty_ok_response()


@API.resource('/api/v1/auth/reset')
class ResetPasswordAPI(Resource):
    @ndb.toplevel
    def post(self):
        """Sets new password given by user if he provided valid token
        Notice ndb.toplevel decorator here, so we can perform asynchronous put and sign-in in parallel
        """
        args = rqParse( rqArg('token'      , userVdr='token_span')
                      , rqArg('newPassword', userVdr='password_span', dest='new_password')
                      )
        user_db = User.get_by('token_h', args.token)
        user_db.pwdhash_h = util.password_hash(args.new_password)
        user_db.token_h = util.uuid()
        user_db.verified_p = True
        user_db.put_async()
        auth.signin_user_db(user_db)
        return user_db.to_dict(all=True)

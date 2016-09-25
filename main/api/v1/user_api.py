# coding: utf-8
# pylint: disable=too-few-public-methods, no-self-use, missing-docstring, unused-argument
"""
Provides API logic relevant to users
"""
from flask_restful import Resource
import auth
from security import pwd
from main   import API
from model.user import User#, UserVdr
from flask  import request, g
from api.decorators import model_by_key, user_by_username, authorization_required, admin_required
from api.helpers    import list_response, ok, rqArg, rqParse
from config import DEVELOPMENT
import validators as vdr
import logging

@API.resource('/api/v1/users')
class UsersAPI(Resource):
    """Gets list of users. Uses ndb Cursor for pagination. Obtaining users is executed
    in parallel with obtaining total count via *_async functions
    """
    @admin_required
    def get(self):
        args = rqParse(rqArg('cursor', type=vdr.toCursor)) 
        usersQuery = User.query() \
            .order(-User.created_r) \
            .fetch_page_async(page_size=10, start_cursor=args.cursor)
        
        totalQuery = User.query().count_async(keys_only=True)
        users, next_cursor, more = usersQuery.get_result()
        users = [u.toDict() for u in users]
        return list_response(users, next_cursor, more, totalQuery.get_result())

        
@API.resource('/api/v1/num_users')
class NumUsersAPI(Resource):
    """Gets number of users.
    """
    def get(self):
        if not DEVELOPMENT:
            abort(404) 
        return User.query().count(); # if number gets large, should we be using sharded counter for this?

        
@API.resource('/api/v1/users/<string:username>')
class UserByUsernameAPI(Resource):
    @admin_required
    @user_by_username
    def get(self, username):
        """Loads user's properties. If logged user is admin it loads also non public properties"""
        return g.usr.toDict(publicOnly=not auth.is_admin())


@API.resource('/api/v1/users/<string:key>')
class UserByKeyAPI(Resource):
    @admin_required
    @authorization_required
    @model_by_key
    def put(self, key):
        """Updates user's properties"""
        g.model_db.populate(request.json)
        g.model_db.put()
        return ok()

        
    @admin_required
    @model_by_key
    def delete(self, key):
        """Deletes user"""
        g.model_key.delete()
        return ok()


@API.resource('/api/v1/users/<string:key>/password')
class UserPasswordAPI(Resource):
    @authorization_required
    @model_by_key
    def post(self, key):
        """Changes user's password"""
        args = rqParse( rqArg('currentPassword', vdr=vdr.password_span, dest='current_password')
                      , rqArg('newPassword'    , vdr=vdr.password_span, dest='new_password')
                      )
        # Users who signed up via social networks could have empty password_hash, but they have to be allowed
        # to change it as well - todo : why ? wouldnt we want them to provide email-address with password?
        if g.model_db.pwdhash__ != '' and not g.model_db.has_password(args.current_password):
            raise ValueError('Given password is incorrect.')
        g.model_db.pwdhash__ = pwd.encrypt(args.new_password)
        g.model_db.put()
        return ok()



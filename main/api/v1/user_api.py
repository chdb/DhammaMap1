# coding: utf-8
# pylint: disable=too-few-public-methods, no-self-use, missing-docstring, unused-argument
"""
Provides API logic relevant to users
"""
from flask_restful import Resource
import auth
import util
from main   import API
from model  import User, UserVdr
from flask  import request, g
from pydash import _
from api.decorators import model_by_key, user_by_username, authorization_required, admin_required
from api.helpers    import ArgVdr, list_response, ok, rqArg, rqParse
from config import DEVELOPMENT
import logging

@API.resource('/api/v1/users')
class UsersAPI(Resource):
    """Gets list of users. Uses ndb Cursor for pagination. Obtaining users is executed
    in parallel with obtaining total count via *_async functions
    """
    @admin_required
    def get(self):
        # p = reqparse.RequestParser()
        # p.add_argument('cursor', type=ArgVdr.fn('cursor'))
        # args = p.parse_args()
        args = rqParse(rqArg('cursor', argVdr='cursor')) 
        usersQuery = User.query() \
            .order(-User.created) \
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
        return User.query().count(); # if it gets large, should we be using sharded counter for this?

@API.resource('/api/v1/users/<string:username>')
class UserByUsernameAPI(Resource):
    @admin_required
    @user_by_username
    def get(self, username):
        """Loads user's properties. If logged user is admin it loads also non public properties"""
        # if auth.is_admin():
            # properties = User.get_private_properties()
        # else:
            # properties = User.get_public_properties()
        return g.usr.toDict(all=auth.is_admin())


@API.resource('/api/v1/users/<string:key>')
class UserByKeyAPI(Resource):
    @admin_required
    @authorization_required
    @model_by_key
    def put(self, key):
        """Updates user's properties"""
        update_properties = ['name', 'bio', 'email_', 'location'
                             , 'facebook', 'github','gplus', 'linkedin', 'twitter', 'instagram']
        if auth.is_admin():
            update_properties += ['isVerified_', 'isActive_', 'isAdmin_']

        new_data = _.pick(request.json, update_properties)
        g.model_db.populate(**new_data)
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
        #logging.debug('zzzzzzzzzzzzzzzzzzzzzzzzzzz')
        # p = reqparse.RequestParser()
        # p.add_argument('currentPassword', type=UserVdr.fn('password_span', required=False), dest='current_password')
        # p.add_argument('newPassword', type=UserVdr.fn('password_span')   , dest='new_password')
        # args = p.parse_args()
        # NB we removed:  required=False
        args = rqParse( rqArg('currentPassword', userVdr='password_span', dest='current_password')
                      , rqArg('newPassword'    , userVdr='password_span', dest='new_password')
                      )

        # Users, who signed up via social networks have empty password_hash, so they have to be allowed
        # to change it as well
        if g.model_db.pwdhash__ != '' and not g.model_db.has_password(args.current_password):
            raise ValueError('Given password is incorrect.')
        g.model_db.pwdhash__ = util.password_hash(args.new_password)
        g.model_db.put()
        return ok()



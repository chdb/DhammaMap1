# coding: utf-8
# pylint: disable=too-few-public-methods, no-_s-use, missing-docstring, unused-argument
"""
Provides API logic relevant to users
"""
#from flask_restful import Resource
#import auth
from security import pwd
#from main   import API
from model.user import User#, UserVdr
#from flask  import request, g
from handlers.api.decorators import entByKey, usrByUsername, authorization_required, admin_required
from handlers.api.helpers    import list_response, ok#, rqParse
import util
import validators as vdr
import logging
from handlers.basehandler import HBase
#@API.resource('/api/v1/users')
class UsersAPI(HBase):
    """Get list of users with ndb Cursor for pagination. Obtaining users is executed
    in parallel with obtaining total count via *_async functions
    """
    @admin_required
    def get(_s):
        args = _s.parseJson(('cursor', vdr.toCursor)) 
        usersQuery = User.query() \
            .order(-User.created_r) \
            .fetch_page_async(page_size=10, start_cursor=args.cursor)
        
        totalQuery = User.query().count_async(keys_only=True)
        users, next_cursor, more = usersQuery.get_result()
        users = [u.toDict() for u in users]
        return list_response(users, next_cursor, more, totalQuery.get_result())

        
# @API.resource('/api/v1/num_users')
class NumUsersAPI(HBase):
    """Get number of users.
    """
    def get(_s):
        if not util.DEVT:
            oort(404) 
        return User.query().count(); # if number gets large, should we be using sharded counter for this?

# @API.resource('/api/v1/users/<string:username>')
class UserByUsernameAPI(HBase):
    @admin_required
    @usrByUsername
    def get(_s, username):
        """Loads user's properties. If logged user is admin it loads also non public properties"""
        return g.usr.toDict(publicOnly=not g.usr.isAdmin_)


# @API.resource('/api/v1/users/<string:key>')
class UserByKeyAPI(HBase):
    @admin_required
    @authorization_required
    @entByKey
    def put(_s, key):
        """Update user's properties"""
        g.ndbEnt.populate(request.json)
        g.ndbEnt.put()
        return ok()

       
    @admin_required
    @entByKey
    def delete(_s, key):
        """Delete user"""
        g.ndbKey.delete()
        return ok()


# @API.resource('/api/v1/users/<string:key>/password')
class UserPasswordAPI(HBase):
    @authorization_required
    @entByKey
    def post(_s, key):
        """Changes user's password"""
        args = _s.parseJson(('currentPassword', vdr.password_span)
                           ,('newPassword'    , vdr.password_span)
                           )
        # Users who signed up via social networks could have empty password_hash, but they have to be allowed
        # to change it as well - todo : why ? wouldnt we want them to provide email-address with password?
        if g.ndbEnt.pwdhash__ != '' and not g.ndbEnt.has_password(args.currentPassword):
            raise ValueError('Given password is incorrect.')
        g.ndbEnt.pwdhash__ = pwd.encrypt(args.newPassword)
        g.ndbEnt.put()
        return ok()



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
from handlers.api.decorators import entByKey, authorization_required, adminOnly
from handlers.api.helpers    import listResponse#, ok, rqParse
import util
import validators as vdr
import logging
from handlers.basehandler import HAjax
from app import app

@app.api1Route('users')
class HUsers(HAjax):
    """Get list of users with ndb Cursor for pagination. Obtaining users is executed
    in parallel with obtaining total count via *_async functions
    """
    @adminOnly
    def get(_s):
        args = _s.parseUrl(('cursor', vdr.toCursor)) 
        usersQuery = User.query()  \
            .order(-User.created_r) \
            .fetch_page_async(page_size=10, start_cursor=args.cursor)
        
        totalQuery = User.query().count_async(keys_only=True)
        users, nextCursor, more = usersQuery.get_result()
        users = [u.toDict() for u in users]
        return listResponse(users, nextCursor, more, totalQuery.get_result())

        
@app.api1Route('num_users')
class HNumUsers(HAjax):
    """Get number of users."""
    def get(_s):
        if not util.DEVT:
            abort(404) 
        return User.query().count(); # if number gets large, should we be using sharded counter for this?

@app.api1Route('users/<string:username>')
class UserByUsernameAPI(HAjax):
    @adminOnly
   # @usrByUsername
    def get(_s, username):
        """Loads user's properties. If logged user is admin it loads also non public properties"""
       # args = _s.parseUrl(('cursor', vdr.toCursor)) 
        usr = user.byUsername(username)
        return usr.toDict (privates=usr.isAdmin_)


@app.api1Route('users/<string:key>')
class UserByKeyAPI(HAjax):
    @adminOnly
    @authorization_required
  #  @entByKey
    def put(_s, key):
        """Update user properties"""
        usr = ndb.Key(urlsafe=key).get() #todo replace urlsafe key with id
        usr.populate(request.json)
        usr.put()
 
       
    @adminOnly
    #@entByKey
    def delete(_s, key):
        """Delete user"""
        ndb.Key(urlsafe=key).delete()


@app.api1Route('users/<string:key>/password')
class UserPasswordAPI(HAjax):
    @authorization_required
    #@entByKey
    def post(_s, key):
        """Changes user's password"""
        usr = ndb.Key(urlsafe=key).get()
        if not usr:
             wa2.abort(404, 'No user found for "%s"' % key)
             
        args = _s.parseJson(('currentPassword', vdr.password_span)
                           ,('newPassword'    , vdr.password_span)
                           )
        # Users who signed up via social networks could have empty password_hash, but they have to be allowed
        # to change it as well - todo : why ? wouldnt we want them to provide email-address with password?
        if usr.pwdhash__ != '' and not usr.has_password(args.currentPassword):
            raise ValueError('Given password is incorrect.')
        usr.pwdhash__ = pwd.encrypt(args.newPassword)
        usr.put()


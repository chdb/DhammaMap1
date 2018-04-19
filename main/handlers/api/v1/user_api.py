# coding: utf-8
# pylint: disable=too-few-public-methods, no-self-use, missing-docstring, unused-argument
"""
Provides API logic relevant to users
"""
#from flask_restful import Resource
#import auth
from google.appengine.ext import ndb
from webapp2 import abort

from security import pwd
#from main   import API
from model.mUser import MUser#, UserVdr
#from flask  import request, g
from handlers.api.decorators import authorization_required, adminOnly
from handlers.api.helpers    import listResponse#, ok, rqParse
from handlers.basehandler    import HAjax
#import util
import validators as vdr
#import logging
from app import app
#from config import appCfg


@app.API_1('users')
class HUsers(HAjax):
    """Get list of users with ndb Cursor for pagination. Obtaining users is executed
    in parallel with obtaining total count via *_async functions
    """
    @adminOnly
    def get(_s):
        args = _s.parseUrl(('cursor', vdr.toCursor))
        usersQuery = MUser.query()  \
            .order(-MUser.created_r) \
            .fetch_page_async(page_size=10, start_cursor=args.cursor)
        totalQuery = MUser.query().count_async(keys_only=True)
        users, nextCursor, more = usersQuery.get_result()
        users = [u.toDict() for u in users]
        return listResponse(users, nextCursor, more, totalQuery.get_result())

@app.API_1('num_users')
class HNumUsers(HAjax):
    """Get number of users."""
    def get(_s):
        #logging.info('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ env = %r', appCfg.env)
        if not app.devt:
            abort(404)
        return MUser.query().count() # if number gets large, should we be using sharded counter for this?

@app.API_1(r'users/<username:[a-zA-Z]\w+>')
class UserByUsernameAPI(HAjax):
    @adminOnly
   # @usrByUsername
    def get(_s, username):
        """Load user's properties. If logged user is admin it loads also non public properties"""
       # args = _s.parseUrl(('cursor', vdr.toCursor))
        usr = MUser.byUsername(username)
        return usr.toDict(privates=usr.isAdmin_)


@app.API_1(r'users/<uid:\d+>')
class UserByKeyAPI(HAjax):
    #@adminOnly
    @authorization_required
  #  @entByKey
    def put(_s, uid):
        """Update user properties"""
        #logging.debug('_s: %r',_s)
        #logging.debug('uid: %r',uid)
        #usr = ndb.Key(urlsafe=key).get() #todo replace urlsafe key with id
        usr = MUser.get_by_id(int(uid))
        usr.populate(_s.request.json)
        usr.put()

    @adminOnly
    #@entByKey
    def delete(_s, uid):
        """Delete user"""
        ndb.Key(MUser, int(uid)).delete()


@app.API_1(r'users/<uid:\d+>/password')
class UserPasswordAPI(HAjax):
    @authorization_required
    #@entByKey
    def post(_s, uid):
        """Change user's password"""
        usr = MUser.get_by_id(int(uid))
        if not usr:
            abort(404, 'No user found for "%s"' % uid)

        args = _s.parseJson( ('currentPassword', vdr.password_span)
                           , ('newPassword'    , vdr.password_span)
                           )
        # Users who signed up via social networks could have empty password_hash, but they have to be allowed
        # to change it as well - todo : why ? wouldnt we want them to provide email-address with password?
        if usr.pwdhash__ != '' and not usr.has_password(args.currentPassword):
            raise ValueError('Given password is incorrect.')
        usr.pwdhash__ = pwd.encrypt(args.newPassword)
        usr.put()

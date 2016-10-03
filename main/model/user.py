# coding: utf-8
"""implementation of User model"""
from __future__ import absolute_import

import hashlib
from google.appengine.ext import ndb
from model import base
import util
import config
import logging
import validators as vdr
import random
from security import pwd

##############################################################################
"""Defines CUSTOM validators for user properties. For SPECIFIED user validators see Validator"""

def _userExists (propName, value, errmsg, flip=False): 
    """Validates that at least one User entity exists with given value for given property-name """
    usr = User.get_by(propName, value) # todo this is an expensive way, see: get_by() - instead use a key
    if (usr is None) != flip:
        raise ValueError(errmsg)
    return value
    
def _noUserExists (propName, value, errmsg) : return _userExists(propName, value, errmsg, flip=True) 

def tokenExistsVdr (token)   : return _userExists  ('token'     , token        ,'Sorry, your token is invalid or expired.') # not called in current codebase
def emailExistsVdr (email)   : return _userExists  ('email_ci__', email.lower(),'This email address is not recognised. Please try again')
def emailUniqueVdr (email)   : return _noUserExists('email_ci__', email.lower(),'Sorry, this email address is already taken.')
def usrnameUniqueVdr(username):return _noUserExists('username'  , username     ,'Sorry, this username is already taken.')

############################################################################
class NotUnique (ValueError): 
    pass
 
class AuthId (ndb.Model):
    """AuthID holds a user's auth id - an identifying string used for login.
    But the string is saved as the id of the entity's key - not in a property.
    We model a many to one relationship - one user may have multiple authIDs, 
    but each will have the same userId preoperty 
    and each authId key string must have different prefix (before ':'). 
    Examples:
         - own:myusername
         - ema:myemail@example.com
         - google:g-username
         - yahoo:y-username
    Each auth_id must be unique across all users - not already taken by any other user
    """
    userId = ndb.IntegerProperty() # the Key for the 
    
    @classmethod
    #@ndb.transactional #todo - commented out - because _create is private and we only call it from a transactional User.create() - is this ok  ?
    def create (C, authId, userId): 
        ''' create the AuthKey this keyStr, 
            else if it already exists, raise NotUnique
         '''
        assert ':' in authId
        k = ndb.Key(C, authId)
        ent = k.get() 
        if ent is not None:
            logging.info('This authId key already exists: %s' % keyStr)
            raise NotUnique
        ent = C(userId=userId)
        ent.key = k
        ent.put()

    
    @staticmethod
    def authId (prefix, id):
        assert prefix.endswith(':')
        return prefix + id

    @staticmethod
    def ownId (username):   return authId ('own:', username)
    @staticmethod
    def emailId (ema):      return authId ('ema:', username)

#############################################################
class User(base.ndbModelBase):
    """A class describing datastore user."""
    name        = ndb.StringProperty (validator=vdr.name_span.fn)
    username    = ndb.StringProperty (validator=vdr.username_span.fn, required=True)
    email_      = ndb.StringProperty (validator=vdr.email_rx.fn)
    email_ci__  = ndb.ComputedProperty(lambda _s: _s.email_.lower() if _s.email_ else None) #for case-insensitive searching
    authIDs_    = ndb.StringProperty (repeated=True)                                                   #private
    permissions_= ndb.StringProperty (repeated=True)                                                   #private
    isActive_   = ndb.BooleanProperty(default= True)                                                   #private
    isAdmin_    = ndb.BooleanProperty(default=False)   #todo: replace with a entry in permissions_ ?   #private
    isVerified_ = ndb.BooleanProperty(default=False)                                                   #private
    token__     = ndb.StringProperty ()                                                       #hidden
    pwdhash__   = ndb.StringProperty ()    # None for users with only 3rd party auth                                                   #hidden
    bio         = ndb.StringProperty (validator=vdr.bio_span.fn)
    location    = ndb.StringProperty (validator=vdr.location_span.fn)
    
 ##   authProviders = ndb.StructuredProperty( AuthProvider, repeated=True) 
    authIds  = ndb.StringProperty (repeated=True) # list of IDs. EG for third party auth, eg 'google:userid'. UNIQUE.
    
    
# class User (ndb.model):
     # pwdhash__  = ndb.StringProperty () # Hashed password string. NB not a required prop because third party authentication doesn't use password.

    @staticmethod
    @ndb.transactional(xg=True)
    def create (authId, **ka):
        ''' Use this method. Dont simply call    User(**ka).put()
            Otherwise DataStore becomes incoherent '''
        user = User (authIds=[authId], **ka)
        key = user.put()
        AuthId.create (authId, key.id())
        return user
        
    @ndb.transactional(xg=True)
    def mergeUsers (_s, authId):
        '''Suppose you want to add an existing authId   authId1 -> user1 with id2'''
        raise NotImpemented
        
    @ndb.transactional(xg=True)
    def addNewAuthId (_s, authId):
        ''' Use this method. Dont simply call:  _s.authIds.append (authId)
            Otherwise DataStore becomes incoherent 
            The authId should be a new one, if not Raises NotUnique 
            NB If authId is not new,ie its already associated with a user, 
            then you need to call mergeUsers() '''
        if authId in _s.authIds:
            logging.warning ('The user already has this authID: %s', authID)
        else: 
            userId = _s._key.id()
            AuthId.create (authId, userId)
            _s.authIds.append (authId)
 
    @staticmethod
    def _deleteAuthId (authId):
        k = ndb.Key (AuthId, authId) 
        k.delete()
    
    @ndb.transactional(xg=True)
    def removeAuthId (_s, authId):
        ''' Use this method. Dont simply call:  _s.authIds.remove (authId)
            Otherwise DataStore becomes incoherent '''
        if authId not in _s.authIds:
            logging.warning ('The user does not have this authID: %s', authID)
        else:
            _s._deleteAuthId (authId)
            _s.authIds.remove (authId)
        
    @ndb.transactional(xg=True)
    def delete (_s):
        ''' Use this method to delete User and associated authIds. 
            Dont simply call:   _s._key.delete()
            Otherwise DataStore becomes incoherent '''
        for a in _s.authIds:
            _s._deleteAuthId (a)
        _s._key.delete()

#############################################################

        
# class AuthProvider (ndb.Model):
    # name   = ndb.StringProperty ()
    # id     = ndb.StringProperty (validator=vdr.social_span.fn)
    
   
    @staticmethod
    def randomAuthIds():
        aps = []
        for ap in config.CONFIG_DB.authProviders:
            if random.choice((True, False)):
                #aps.append( AuthProvider(name=ap.name, id=util.randomB64()))
                aps.append( config.authNames[ap.name]+util.randomB64())
        util.debugList(aps, 'random Auth Providers')
        return aps
        
    def has_password(self, password):
        """Test if user has the correct password"""
        valid, new_hash = pwd.verify_and_update(password, self.pwdhash__)
        if valid:
            if new_hash: # update user password hash
                self.pwdhash__ = new_hash
                self.put()
        return valid
                 
    @classmethod
    def is_username_available(cls, username):
        """Tests if user has username is available"""
        return cls.get_by('username', username) is None

    @classmethod
    def get_by_credentials(cls, email_or_username, password):
        """Gets user model instance by email or username with given password"""
        #todo - this code looks a bit crazy!
        try:        
            email_or_username == User.email_ # what is this for? 
        except ValueError: # how can this exception ever come here? 
            cond = email_or_username == User.username
        else:
            cond = email_or_username == User.email_
        usr = User.query(cond).get()

        if usr and usr.has_password(password):
            return usr
        return None

    def toDict(self, publicOnly=True):
        def avatar_url(self):
            #todo why not 1) just pass the hash to client? and put the url template code in the client
            #     and/or  2) store the hash in user model 
            """Returns gravatar url, created from user's email or username"""
            return '//gravatar.com/avatar/%(hash)s?d=identicon&r=x' % {
                'hash': hashlib.md5((self.email_ or self.username).encode('utf-8')).hexdigest()
                }
    
        d = self.toDict_(publicOnly)
        d['key']        = self.key.urlsafe()
        d['avatar_url'] = avatar_url(self)
        return d


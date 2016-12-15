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
"""Define CUSTOM validators for user properties. For SPECIFIED user validators see Validator"""

def usernameExists(un):
    return AuthId.get_by_id (unameId(un)) is not None
  
def _userExists (aId, errmsg, flip=False): 
    """Validates that at least one User entity exists with given value for given property-name """
    ref = AuthId.get_by_id (aId) 
    if (ref is None) != flip:
        raise ValueError(errmsg)
    return aId[3:]
    
def _noUserExists (aId, errmsg) : return _userExists(aId, errmsg, flip=True) 

#def tokenExistsVdr (token)   : return _userExists  ('token'     , token        ,'Sorry, your token is invalid or expired.') # not called in current codebase
def emailExistsVdr (ema)   : return _userExists  (emailId(ema)  ,'This email address is not recognised. Please try again')
def emailUniqueVdr (ema)   : return _noUserExists(emailId(ema)  ,'Sorry, this email address is already taken.')
def usrnameUniqueVdr(uname): return _noUserExists(unameId(uname),'Sorry, this username is already taken.')

############################################################################
class NotUnique (ValueError): 
    pass
 
class AuthId (ndb.Model):
    """AuthID holds a user's auth id - an identifying string used for login.
    But the string is saved as the id of the entity's key - not in a property.
    We model a many to one relationship - one user may have multiple authIDs, 
    but each will have the same userId property 
    and each authId key string must have different prefix (before ':') as specified by config.authNames 
    Examples:
          _u:myusername
          _e:myemail@example.com
          gg:google-user-id
          yh:yahoo-user-id
    Each auth_id must be unique across all users - not already taken by any other user
    """
    userId = ndb.IntegerProperty() # the Key id for the User entity associated with this AuthID
    
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
            logging.info('This authId key already exists: %s' % authId)
            raise NotUnique
        ent = C(userId=userId)
        ent.key = k
        ent.put()
    
def _authId (prefix, id):
    assert prefix.endswith(':')
    assert prefix in config.authNames
    return prefix + id

def unameId (username): return _authId ('_u:', username)
def emailId (ema):      return _authId ('_e:', ema.lower()) #NB we convert to lower so searches are case-insensitive
                                                            # ...otoh User.email_ is case-sensitive and we use this for sending emails etc
    
def _byAuthId (aId):      
    aId = AuthId.get_by_id (aId)
    if aId:
        #logging.debug('uid = %r', uid)
        return User.get_by_id (aId.userId)
    return None
    
def byEmail    (ema):      return _byAuthId (emailId (ema))
def byUsername (userName): return _byAuthId (unameId (userName))
        
def byCredentials(email_or_username, password):
    """Gets user model instance by email or username with given password"""
    #todo - this code looks a bit crazy!
    # try:        
        # email_or_username == User.email_ # what is this for? 
    # except ValueError: # how can this exception ever come here? 
        # cond = email_or_username == User.username
    # else:
        # cond = email_or_username == User.email_
    # usr = User.query(cond).get()
    
    usr =  byEmail   (email_or_username) \
        or byUsername(email_or_username)
    logging.debug('usr = %r', usr)
    if usr and usr.has_password(password):
        return usr
    return None

def getHash(ema):
    #todo why not 1) just pass the hash to client? and put the url template code in the client
    #     and/or  2) store the hash in user model 
    """Returns hash created from user's email or username for the gravatar url,"""
    return hashlib.md5(ema.lower().encode('utf-8')).hexdigest()
    
        
def randomAuthIds():
    aps = []
    for ap in config.CONFIG_DB.authProviders:
        if random.choice((True, False)):
            #aps.append( AuthProvider(name=ap.name, id=util.randomB64()))
            aps.append( config.authNames[ap.name]+util.randomB64())
    util.debugList(aps, 'random Auth Providers')
    return aps

#############################################################
class User(base.ndbModelBase):
    """A class describing datastore user."""
#    name        = ndb.StringProperty (validator=vdr.name_span.fn)
    username    = ndb.StringProperty (indexed=False, required=True, validator=vdr.username_span.fn)
    email_      = ndb.StringProperty (indexed=False, required=True, validator=vdr.email_rx.fn)
#    email_ci__  = ndb.ComputedProperty(lambda _s: _s.email_.lower() if _s.email_ else None) #for case-insensitive searching
#    authIDs_    = ndb.StringProperty (repeated=True)                                                   #private
#    permissions_= ndb.StringProperty (repeated=True)                                                   #private
    isActive_   = ndb.BooleanProperty(indexed=False, default= True)                                                   #private
    isAdmin_    = ndb.BooleanProperty(indexed=False, default=False)   #todo: replace with a entry in permissions_ ?   #private
    isVerified_ = ndb.BooleanProperty(indexed=False, default=False)                                                   #private
    token__     = ndb.StringProperty (indexed=False)                                                       #hidden
    pwdhash__   = ndb.StringProperty (indexed=False)    # None for users with only 3rd party auth                                                   #hidden
    bio         = ndb.StringProperty (indexed=False, validator=vdr.bio_span.fn)
    location    = ndb.StringProperty (indexed=False, validator=vdr.location_span.fn)
    hash        = ndb.StringProperty (indexed=False)
    authIds     = ndb.StringProperty (indexed=False, repeated=True) # list of IDs. EG for third party auth, eg 'google:userid'. UNIQUE.
    

# class User (ndb.model):
     # pwdhash__  = ndb.StringProperty () # Hashed password string. NB not a required prop because third party authentication doesn't use password.

    @staticmethod
    @ndb.transactional(xg=True)
    def create (**ka):
        ''' Use this method. Dont simply call    User(**ka).put()
            Otherwise DataStore becomes incoherent '''
        #assert 'email_' in ka, 'all accounts must be created with an email' 
        util.debugDict(ka, 'ka')
        ids = ka.get('authIds',[])
        ema = ka['email_']
        un  = ka['username']
        ids.append(emailId(ema))
        ids.append(unameId(un))
        ka['authIds'] = ids
        ka['hash'] = getHash(ema)
        #if 'username' in ka:
        user = User (**ka)
        key = user.put()
        for i in ids:
            AuthId.create (i, key.id())
        return user
        
    @ndb.transactional(xg=True)
    def mergeUsers (_s, authId):
        '''Suppose you want to add an existing authId   authId1 -> user1 with id2'''
        raise NotImplemented
        
    @ndb.transactional(xg=True)
    def addNewAuthId (_s, authId):
        ''' Use this method. Dont simply call:  _s.authIds.append (authId)
            Otherwise DataStore becomes incoherent 
            The authId should be a new one, if not Raises NotUnique 
            NB If authId is not new,ie its already associated with a user, 
            then you need to call mergeUsers() '''
        prefix = authId[:3]
        for i in _s.authIds:
            if i.startswith(prefix):
                logging.warning ('The user already has authID: %s', i)
                raise Exception
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

        
    def has_password(_s, password):
        """Test if user has the correct password"""
        logging.debug('pwd = %r', password)
        valid, new_hash = pwd.verify_and_update(password, _s.pwdhash__)
        if valid:
            if new_hash: # update user password hash
                _s.pwdhash__ = new_hash
                _s.put()
        return valid
                 
    # @classmethod
    # def is_username_available(cls, username):
        # """Tests if user has username is available"""
        # return cls.get_by('username', username) is None


    def toDict(_s, publicOnly=True):
    
        d = _s.toDict_(publicOnly)
        d['_k'] = _s.key.urlsafe() #needed for client calls to Restangular.one(...).get()
        
        # i = next(i for i in d['authIds'] if i.startswith('_u:'))
        # if i: 
            # d['username'] = i[3:]
            
        util.debugDict(d, 'user dict 1 ')
        ids = d.get('authIds',[])
        d['authIds'] = [ i for i in ids if not i.startswith('_')]
                                
        util.debugDict(d, 'user dict ')
        return d


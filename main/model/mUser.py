# coding: utf-8
"""implementation of MUser model"""
from __future__ import absolute_import

import hashlib
from google.appengine.ext import ndb
from model import mBase
import util
import config
import logging
import validators as vdr
import random
from security import pwd
import webapp2 as wa2

##############################################################################
"""Define CUSTOM validators for user properties. For SPECIFIED user validators see Validator"""

def usernameExists(un):
    return AuthId.get_by_id(unameId(un)) is not None
  
def _userExists(aId, errmsg, flip=False): 
    """Validates that at least one MUser entity exists with given value for given property-name """
    ref = AuthId.get_by_id(aId) 
    if(ref is None) != flip:
        wa2.abort(422, errmsg)
    return _Id(aId)
    
def _noUserExists(aId, errmsg) : return _userExists(aId, errmsg, flip=True) 

#def tokenExistsVdr(token)   : return _userExists ('token'     , token        ,'Sorry, your token is invalid or expired.') # not called in current codebase
def emailExistsVdr(ema)   : return _userExists (emailId(ema)  ,'That email address is not recognised. Please try again')
def emailUniqueVdr(ema)   : return _noUserExists(emailId(ema)  ,'Sorry, that email address is already taken.')
def usrnameUniqueVdr(uname): return _noUserExists(unameId(uname),'Sorry, that username is already taken.')

############################################################################
class NotUnique(ValueError): 
    pass
 
class AuthId(ndb.Model):
    """A user's authId key string, an identifying string used for login, held as the idStr of the entity's key - not in a property.
    One user may have multiple authIDs, so this represents a many-to-one relationship - AuthId to MUser. Each AuthId having the same 
    userId property. Each authId key string must have a different prefix(before ':') as specified by config.authNames 
    Examples:
          _u:myusername
          _e:myemail@example.com
          gg:google-user-idStr
          yh:yahoo-user-idStr
    Each auth_id must be unique across all users - not already taken by any other user
    """
    userId = ndb.IntegerProperty() # the Key id for the MUser entity associated with this AuthID
    
    @classmethod
    #@ndb.transactional #todo - commented out - because _create is private and we only call it from a transactional MUser.create() - is this ok  ?
    def create(C, authId, userId): 
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
    
def _authId(prefix, idStr):
    assert prefix.endswith(':')
    assert prefix in config.authNames
    assert len(prefix) == 3
    return prefix + idStr
    
def _Id(authId): return authId[3:]

def unameId(username): return _authId('_u:', username)
def emailId(ema):      return _authId('_e:', ema.lower()) #NB we convert to lower so searches are case-insensitive
                                                            # ...otoh MUser.email_ is case-sensitive and we use this for sending emails etc
    
def _byAuthId(authId):      
    aId = AuthId.get_by_id(authId)
    if aId:
        #logging.debug('uid = %r', uid)
        return MUser.get_by_id(aId.userId)
    return None
        #wa2.abort(404, 'No user found for "%s"' % authId)
     
        


def getHash(ema):
    #todo md5 is recommended by gravatar but has poor reputation - 
    #   so if this means an attacker could possibly reverse the hash to extract email address  
    #   then can we not replace md5 with a better algorithm but of course the gravatar icon would be different  
    
    """Returns hash created from user's email or username for the gravatar url,"""
    return hashlib.md5(ema.lower().encode('utf-8')).hexdigest()
    
        
def randomAuthIds():
    aids = []
    for ap in config.authNames:
        if ap.endswith(':'):
            if random.choice((True, False)):
                #aps.append( AuthProvider(name=ap.name, id=util.randomB64()))
                aids.append(ap + util.randomB64(8))
    util.debugList(aids, 'random Auth Providers')
    return aids

#############################################################
class MUser(mBase.ndbModelBase):
    """A class describing datastore user."""
#    name        = ndb.StringProperty(validator=vdr.name_span.fn)
    username    = ndb.StringProperty(indexed=False, required=True, validator=vdr.username_span.fn)
    email_      = ndb.StringProperty(indexed=False, required=True, validator=vdr.email_rx.fn)
#    email_ci__  = ndb.ComputedProperty(lambda _s: _s.email_.lower() if _s.email_ else None) #for case-insensitive searching
#    authIDs_    = ndb.StringProperty(repeated=True)                                                   #private
#    permissions_= ndb.StringProperty(repeated=True)                                                   #private
    isActive_   = ndb.BooleanProperty(indexed=False, default=True)                                                   #private
    isAdmin_    = ndb.BooleanProperty(indexed=False, default=False)   #todo: replace with a entry in permissions_ ?   #private
    isVerified_ = ndb.BooleanProperty(indexed=False, default=False)                                                   #private
    token__     = ndb.StringProperty(indexed=False)                                                       #hidden
    pwdhash__   = ndb.StringProperty(indexed=False)    # None for users with only 3rd party auth                                                   #hidden
    bio         = ndb.StringProperty(indexed=False, validator=vdr.bio_span.fn)
    location    = ndb.StringProperty(indexed=False, validator=vdr.location_span.fn)
    emaHash     = ndb.StringProperty(indexed=False)
    authIds     = ndb.StringProperty(indexed=False, repeated=True) # list of IDs. EG for third party auth, eg 'google:userid'. UNIQUE.
    

# class MUser(ndb.model):
     # pwdhash__  = ndb.StringProperty() # Hashed password string. NB not a required prop because third party authentication doesn't use password.

    def id(_s):              return _s._key.id()
        
    @staticmethod
    def byEmail   (ema):     return _byAuthId(emailId(ema))

    @staticmethod
    def byUsername(userName):return _byAuthId(unameId(userName))

    @staticmethod
    def byCredentials(email_or_username, password):
        """Gets user model instance by email or username with given password"""
        #todo - this code looks a bit crazy!
        # try:        
            # email_or_username == MUser.email_ # what is this for? 
        # except ValueError: # how can this exception ever come here? 
            # cond = email_or_username == MUser.username
        # else:
            # cond = email_or_username == MUser.email_
        # usr = MUser.query(cond).get()
        
        usr =  MUser.byEmail  (email_or_username) \
            or MUser.byUsername(email_or_username)
        logging.debug('usr = %r', usr)
        if usr and usr.has_password(password):
            return usr
        return None

    @staticmethod
    @ndb.transactional(xg=True)
    def create(**ka):
        ''' Use this method. Dont simply call    MUser(**ka).put()
            Otherwise DataStore becomes incoherent '''
        #assert 'email_' in ka, 'all accounts must be created with an email' 
  #      util.debugDict(ka, 'ka')
        ids = ka.get('authIds',[])
        ema = ka['email_']
        un  = ka['username']
        ids.append(emailId(ema))
        ids.append(unameId(un))
        ka['authIds'] = ids
        ka['emaHash'] = getHash(ema)
        ka['pwdhash__'] = pwd.encrypt(ka.pop('password'))
        
        #if 'username' in ka:
        user = MUser(**ka)
        key = user.put()
        for i in ids:
            AuthId.create(i, key.id())
        return user
        
    @ndb.transactional(xg=True)
    def mergeUsers(_s, authId):
        '''Suppose you want to add an existing authId   authId1 -> user1 with id2'''
        raise NotImplemented
        
    @ndb.transactional(xg=True)
    def addNewAuthId(_s, authId):
        ''' Use this method. Dont simply call:  _s.authIds.append(authId)
            Otherwise DataStore becomes incoherent 
            The authId should be a new one, if not Raises NotUnique 
            NB If authId is not new,ie its already associated with a user, 
            then you need to call mergeUsers() '''
        prefix = authId[:3]
        for i in _s.authIds:
            if i.startswith(prefix):
                logging.warning('The user already has authID: %s', i)
                raise Exception
        userId = _s._key.id()
        AuthId.create(authId, userId)
        _s.authIds.append(authId)
 
    @staticmethod
    def _deleteAuthId(authId):
        k = ndb.Key(AuthId, authId) 
        k.delete()
    
    @ndb.transactional(xg=True)
    def removeAuthId(_s, authId):
        ''' Use this method. Dont simply call:  _s.authIds.remove(authId)
            Otherwise DataStore becomes incoherent '''
        if authId not in _s.authIds:
            logging.warning('The user does not have this authID: %s', authID)
        else:
            _s._deleteAuthId(authId)
            _s.authIds.remove(authId)
        
    @ndb.transactional(xg=True)
    def delete(_s):
        ''' Use this method to delete MUser and associated authIds. 
            Dont simply call:   _s._key.delete()
            Otherwise DataStore becomes incoherent '''
        for a in _s.authIds:
            _s._deleteAuthId(a)
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


    def toDict(_s, privates=True):
    
        d = _s.toDict_(privates)
        d['uid'] = _s.key.id() #needed for client calls to Restangular.one(...).get()
        
        # i = next(i for i in d['authIds'] if i.startswith('_u:'))
        # if i: 
            # d['username'] = i[3:]
            
       # util.debugDict(d, 'user dict 1 ')
        ids = d.get('authIds',[])
        d['authIds'] = [ i for i in ids if not i.startswith('_')]
                                
    #    util.debugDict(d, 'user dict ')
        return d


# coding: utf-8
"""implementation of User model"""
from __future__ import absolute_import

import hashlib
from google.appengine.ext import ndb
import model
import util
import config
import logging
import validators as vdr
import random
from security import pwd

##############################################################################
"""Defines CUSTOM validators for user properties. For SPECIFIED user validators see Validator"""

def _userExists (name, val, errmsg, flip=False): 
    """Validates that at least one User entity exists with given value for given property-name """
    usr = User.get_by(name, token) # todo this is an expensive way, see: get_by() - instead use a key
    if (usr is None) != flip:
        raise ValueError(errmsg)
    return token
    
def _noUserExists (name, val, errmsg) : return _userExists('token', token, errmsg, flip=True) 

def tokenExistsVdr (token)   : return _userExists  ('token', token, 'Sorry, your token is invalid or expired.')
def emailExistsVdr (email)   : return _userExists  ('email_', email, 'This email address is not recognised. Please try again')
def emailUniqueVdr (email)   : return _noUserExists('email_', email, 'Sorry, this email address is already taken.')
def usrnameUniqueVdr(username):return _noUserExists('username', username, 'Sorry, this username is already taken.')

############################################################################

class AuthProvider (ndb.Model):
    name   = ndb.StringProperty ()
    id     = ndb.StringProperty (validator=vdr.social_span.fn)
    
   
class User(model.ndbModelBase):
    """A class describing datastore user."""
    name        = ndb.StringProperty (validator=vdr.name_span.fn)
    username    = ndb.StringProperty (validator=vdr.username_span.fn, required=True)
    email_      = ndb.StringProperty (validator=vdr.email_rx.fn) #private
    authIDs_    = ndb.StringProperty (repeated=True)                                                   #private
    permissions_= ndb.StringProperty (repeated=True)                                                   #private
    isActive_   = ndb.BooleanProperty(default= True)                                                   #private
    isAdmin_    = ndb.BooleanProperty(default=False)   #todo: replace with a permissions_ property?   #private
    isVerified_ = ndb.BooleanProperty(default=False)                                                   #private
    token__     = ndb.StringProperty ()                                                       #hidden
    pwdhash__   = ndb.StringProperty ()                                                       #hidden
    bio         = ndb.StringProperty (validator=vdr.bio_span.fn)
    location    = ndb.StringProperty (validator=vdr.location_span.fn)
    
    authProviders = ndb.StructuredProperty( AuthProvider, repeated=True) 
    
    @staticmethod
    def randomAuthProvs():
        aps = []
        for ap in config.CONFIG_DB.authProviders:
            if random.choice((True, False)):
                aps.append( AuthProvider(name=ap.name, id=util.randomB64()))
        util.debugList(aps, 'random Auth Providers')
        return aps
        
    def has_password(self, password):
        """Test if user has the correct password"""
        valid, new_hash = pwd.verify_and_update(password, self.pwdhash__)
        if valid:
            if new_hash:
                # update user password hash
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
            #its either True or False but how can it possibly throw?If theres no value for email_ then User.email_ evaluates to None or '' and the expression its False
        except ValueError: # how can this exception ever come here? 
            cond = email_or_username == User.username
            logging.debug('@@@@@@@@@@@@@@ cond 1 = %r', cond)
        else:
            cond = email_or_username == User.email_
            logging.debug('@@@@@@@@@@@@@@ cond 2 = %r', cond)
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


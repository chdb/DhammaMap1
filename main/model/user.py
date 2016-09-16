# coding: utf-8
"""Provides implementation of User model and User"""
from __future__ import absolute_import

import hashlib
from google.appengine.ext import ndb
import model
import util
import config
import logging
import validators as vdrs
##############################################################################
"""Defines validators for user properties. For detailed description see Validator"""
name_span     = [0, 100]
username_span = [3, 40]
password_span = [6, 70]
bio_span      = [0, 140]
location_span = [0, 70]
social_span   = [0, 50]
email_rx  = config.EmailRegEx

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
    
class User(model.ndbModelBase):
    """A class describing datastore user."""
    name        = ndb.StringProperty (default=''   , validator=vdrs.fn(name_span))
    username    = ndb.StringProperty (required=True, validator=vdrs.fn(username_span))
    email_      = ndb.StringProperty (default=''   , validator=vdrs.fn(email_rx, required=False)) #private
    authIDs_    = ndb.StringProperty (repeated=True)                                                   #private
    permissions_= ndb.StringProperty (repeated=True)                                                   #private
    isActive_   = ndb.BooleanProperty(default= True)                                                   #private
    isAdmin_    = ndb.BooleanProperty(default=False)   #todo: replace with a permissions_ property?   #private
    isVerified_ = ndb.BooleanProperty(default=False)                                                   #private
    token__     = ndb.StringProperty (default='')                                                       #hidden
    pwdhash__   = ndb.StringProperty (default='')                                                       #hidden
    bio         = ndb.StringProperty (default='', validator=vdrs.fn(bio_span))
    location    = ndb.StringProperty (default='', validator=vdrs.fn(location_span))
    
    #todo use StructuredProperty
    facebook    = ndb.StringProperty (default='', validator=vdrs.fn(social_span))
    twitter     = ndb.StringProperty (default='', validator=vdrs.fn(social_span))
    gplus       = ndb.StringProperty (default='', validator=vdrs.fn(social_span))
    instagram   = ndb.StringProperty (default='', validator=vdrs.fn(social_span))
    linkedin    = ndb.StringProperty (default='', validator=vdrs.fn(social_span))
    github      = ndb.StringProperty (default='', validator=vdrs.fn(social_span))
    # todo: do we really need default='' on every StringProperty ? If so creat a custom StringProperty ?
    # But whats so wrong with the default behavior IE default=None?
    
    #@property
    def has_password(self, password):
        """Tests if user has given password"""
        return self.pwdhash__ == util.password_hash(password)

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
            logging.debug('@@@@@@@@@@@@@@ cond 1 = %r', cond)
        else:
            cond = email_or_username == User.email_
            logging.debug('@@@@@@@@@@@@@@ cond 2 = %r', cond)
        usr = User.query(cond).get()

        if usr and usr.pwdhash__ == util.password_hash(password): # todo timer attack vuln
            return usr
        return None

    def toDict(self, publicOnly=True):
        
        #todo why not 1) just pass the hash to client
        #             2) store the hash in user model ? and put the url template code in the client
        def avatar_url(self):
            """Returns gravatar url, created from user's email or username"""
            return '//gravatar.com/avatar/%(hash)s?d=identicon&r=x' % {
                'hash': hashlib.md5((self.email_ or self.username).encode('utf-8')).hexdigest()
                }
    
        d = self.toDict_(publicOnly)
        d['key']        = self.key.urlsafe()
        d['avatar_url'] = avatar_url(self)
                # ka = _.pick(ka, update_properties)
        # logging.debug('User.toDict() +++++++++++++++++++++++++++++++++++')
        # for k,v in d.iteritems():
            # logging.debug('%r : %r', k,v)
        # logging.debug('+++++++++++++++++++++++++++++++++++++++++++')

        return d

    # def populate_(s_, ka):
        # update_properties = [ 'name', 'bio', 'email_', 'location'
                            # , 'facebook', 'github','gplus', 'linkedin', 'twitter', 'instagram']
        # if auth.is_admin():
            # update_properties += ['isVerified_', 'isActive_', 'isAdmin_']

        # ka = _.pick(ka, update_properties)
        # logging.debug('exclude +++++++++++++++++++++++++++++++++++')
        # for k,v in ka.iteritems():
            # if k.endswith('_'):
                # logging.debug('%r', k)
        # logging.debug('+++++++++++++++++++++++++++++++++++++++++++')
         
        # ka = {k:v for k,v in ka.iteritems() if k.endswith('_')} # also excludes user changing own email
        
        # s_.populate(**ka)

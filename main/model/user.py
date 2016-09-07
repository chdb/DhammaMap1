# coding: utf-8
"""Provides implementation of User model and User"""
from __future__ import absolute_import

import hashlib
from google.appengine.ext import ndb
import model
import util
import config

class UserVdr(model.Validator):
    """Defines validators for user properties. For detailed description see Validator"""
    name_span     = [0, 100]
    username_span = [3, 40]
    password_span = [6, 70]
    bio_span      = [0, 140]
    location_span = [0, 70]
    social_span   = [0, 50]
    email_rx  = config.EmailRegEx

    @classmethod
    def existing_token(cls, token):
        """Validates if given token is in datastore"""
        usr = User.get_by('token', token)
        if not usr:
            raise ValueError('Sorry, your token is either invalid or expired.')
        return token

    @classmethod
    def existing_email(cls, email):
        """Validates if given email is in datastore"""
        usr = User.get_by('email_', email)
        if not usr:
            raise ValueError('This email is not in our database.')
        return email

    @classmethod
    def unique_email(cls, email):
        """Validates if given email is not in datastore"""
        usr = User.get_by('email_', email)
        if usr:
            raise ValueError('Sorry, this email is already taken.')
        return email

    @classmethod
    def unique_username(cls, username):
        """Validates if given username is not in datastore"""
        if not User.is_username_available(username):
            raise ValueError('Sorry, this username is already taken.')
        return username


class User(model.ndbModelBase):
    """A class describing datastore user."""
    name        = ndb.StringProperty (default=''   , validator=UserVdr.fn('name_span'))
    username    = ndb.StringProperty (required=True, validator=UserVdr.fn('username_span'))
    email_     = ndb.StringProperty (default=''   , validator=UserVdr.fn('email_rx', required=False)) #private
    authIDs_   = ndb.StringProperty (repeated=True)                                                   #private
    permissions_=ndb.StringProperty (repeated=True)                                                   #private
    isActive_    = ndb.BooleanProperty(default= True)                                                   #private
    isAdmin_     = ndb.BooleanProperty(default=False)   #todo: replace with a permissions_ property?   #private
    isVerified_  = ndb.BooleanProperty(default=False)                                                   #private
    token__     = ndb.StringProperty (default='')                                                       #hidden
    pwdhash__   = ndb.StringProperty (default='')                                                       #hidden
    bio         = ndb.StringProperty (default='', validator=UserVdr.fn('bio_span'))
    location    = ndb.StringProperty (default='', validator=UserVdr.fn('location_span'))
    facebook    = ndb.StringProperty (default='', validator=UserVdr.fn('social_span'))
    twitter     = ndb.StringProperty (default='', validator=UserVdr.fn('social_span'))
    gplus       = ndb.StringProperty (default='', validator=UserVdr.fn('social_span'))
    instagram   = ndb.StringProperty (default='', validator=UserVdr.fn('social_span'))
    linkedin    = ndb.StringProperty (default='', validator=UserVdr.fn('social_span'))
    github      = ndb.StringProperty (default='', validator=UserVdr.fn('social_span'))
    # todo: do we really need default='' on every StringProperty ? If so creat a custom StringProperty ?
    # But whats so wrong with the default behavior IE default=None?
    
    # PUBLIC_PROPERTIES = ['avatar_url', 'name', 'username', 'bio', 'location',
                         # 'facebook', 'twitter', 'gplus', 'linkedin', 'github', 'instagram']

    # PRIVATE_PROPERTIES = ['isAdmin_', 'isActive_', 'authIDs_', 'email_', 'permissions_', 'isVerified_']
    #todo:  code dup of prop names - just use ndb.model._properties() and do some string processing
    #       distinguish private ones with suffix '_' EG 'email_'
    #       distinguish hidden ones with suffix '__' EG 'token__'
    #       pseudo-properties EG avatar_url will still need to be added manually (presumably)
    #   
    #PubProps, PriProps = selectFrom (_properties(), PseudoProps)
    #
    #PseudoProps = ['avatar_url']
    @property
    def avatar_url(self):
        """Returns gravatar url, created from user's email or username"""
        return '//gravatar.com/avatar/%(hash)s?d=identicon&r=x' % {
            'hash': hashlib.md5(
                (self.email_ or self.username).encode('utf-8')).hexdigest()
        }

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
        try:
            email_or_username == User.email_
        except ValueError:
            cond = email_or_username == User.username
        else:
            cond = email_or_username == User.email_
        usr = User.query(cond).get()

        if usr and usr.pwdhash__ == util.password_hash(password):
            return usr
        return None

    def toDict(self, all=False):
        d = self.toDict_(all)
        d['key'] = self.key.urlsafe()
        # d['id']  = self.key.id()
        return d




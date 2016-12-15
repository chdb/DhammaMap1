# coding: utf-8
"""Provides implementation of Config"""
from __future__ import absolute_import

from google.appengine.ext import ndb
from google.appengine.api import app_identity 
#import config
from model import base #, ConfigAuth
import util
import logging

# class AuthProvider (ndb.Model):
    # name   = ndb.StringProperty()
    # id     = ndb.StringProperty()
    # secret_= ndb.StringProperty()
    
# def _apDict (apList):
    ##convert authProviders from list to dict keyed on name
    # apDict = {} 
    # for ap in apList:
        # util.debugList(ap, ' ap         ################       ')
        # apDict[ap['name']] = {k:v for k,v in ap.iteritems() if k != 'name'}
    # return apDict


# def _apList (apDict):
    ##convert back to list
    # apList = [] 
    # for k,ap in apDict.iteritems():
         # ap['name'] = k
         # apList.append(ap)
    # return apList
    
class Config(base.ndbModelBase):
    """A class describing datastore config."""
#   analytics_id       = ndb.StringProperty()    # Google Analytics ID
    site_name          = ndb.StringProperty(default=app_identity.get_application_id())  # Webapp name
    description        = ndb.StringProperty()    # goes into meta data in html header for Webapp description
    admin_email_       = ndb.StringProperty(default='abc@xyz')    # private: Admin's email, where feedback will be sent
#    flask_secret       = ndb.StringProperty(default=util.randomB64()) 
    recaptcha_forms    = ndb.StringProperty(repeated=True) # List of form names where recaptcha is enabled
#    recaptcha_secret   = ndb.StringProperty()
#    recaptcha_id       = ndb.StringProperty()
#    salt_              = ndb.StringProperty(default=util.randomB64()) # todo Arent we stuffed if old value gets overwritten ? protest from overwriting or Instead keep old vals as entities Model:Salt (val, date )
    verify_email       = ndb.BooleanProperty(default=True) # Whether to verify emails of newly registered users
    notify_on_new_user_= ndb.BooleanProperty(default=True) # Whether to send email to admin if user signs up
    
#    authProviders   = ndb.StructuredProperty(AuthProvider, repeated=True) 

    @property
    def has_recaptcha(self):  # pylint: disable=missing-docstring
        return bool(self.recaptcha_secret) # and bool(self.recaptcha_id)

    @classmethod
    def get_master_db(cls):
        """Get config - if entity doesn't exist, it creates new one.
        There's need only for one config - master"""
        
        key = ndb.Key(cls, 'master')
        ent = key.get()
        if ent: 
            return ent # ok found it but if we are in dev - then we must have some test authProviders
        # if util.DEVT and ent and all(i.name for i in ent.authProviders):
            # return ent
            
        # apTestList = []
        ##for i in ['facebook','twitter','google','instagram','linkedin','github']:
                
        # for i in config.authNames:
            # if not i.endswith(':'): # exclude short names
                # apTestList.append( AuthProvider ( name   =i
                                                # , id     =util.randomB64() 
                                                # , secret_=util.randomB64() 
                                                # ))  
        ent = cls()
        ent.key = key
        ent.put()
        return ent

    #def toDict(self, *args, **kwargs):
    def toDict(self, nullVals=False):
        """Creates dict representation of config model plus some other config props """        
        d = self.toDict_(publicOnly=False, nullprops=nullVals)
        d['development'] = util.DEVT
        d['has_feedback']= bool(self.admin_email_) 
      #  d['authProviders'] = _apDict(d['authProviders'])
        
        return d

    def populate(_s, **ka):
        
        if 'authProviders' in ka:
            d1 = ka['authProviders']
            d0 = _apDict(_s.authProviders)
            ka['authProviders'] = _apList(d0.update(d1))
        
        super(Config, _s).populate(**ka)

CONFIG_DB = Config.get_master_db()
    
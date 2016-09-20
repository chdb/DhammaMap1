# coding: utf-8
"""Provides implementation of Config"""
from __future__ import absolute_import

from google.appengine.ext import ndb
import config
from model import ndbModelBase #, ConfigAuth
import util
import logging


class AuthProvider (ndb.Model):
    name   = ndb.StringProperty()
    id     = ndb.StringProperty()
    secret_= ndb.StringProperty()
    
                    
class Config(ndbModelBase):
    """A class describing datastore config."""
    analytics_id       = ndb.StringProperty()    # Google Analytics ID
    site_name          = ndb.StringProperty(default=config.APPLICATION_ID)  # Webapp name
    description        = ndb.StringProperty()    # Webapp description
    admin_email_       = ndb.StringProperty()    # private: Admin's email, where feedback will be sent
    flask_secret       = ndb.StringProperty(default=util.randomB64()) 
    recaptcha_forms    = ndb.StringProperty(repeated=True) # List of form names where recaptcha is enabled
    recaptcha_secret   = ndb.StringProperty()
    recaptcha_id       = ndb.StringProperty()
    salt_              = ndb.StringProperty(default=util.randomB64()) # todo Arent we stuffed if old value gets overwritten ? protest from overwriting or Instead keep old vals as entities Model:Salt (val, date )
    verify_email       = ndb.BooleanProperty(default=True) # Whether to verify emails of newly registered users
    notify_on_new_user_= ndb.BooleanProperty(default=True) # Whether to send email to admin if user signs up
    
    authProviders   = ndb.StructuredProperty( AuthProvider, repeated=True) 

    @property
    def has_recaptcha(self):  # pylint: disable=missing-docstring
        return bool(self.recaptcha_secret) and bool(self.recaptcha_id)

    @classmethod
    def get_master_db(cls):
        """Get config - if entity doesn't exist, it creates new one.
        There's need only for one config - master"""
        
        key = ndb.Key(cls, 'master')
        ent = key.get()
        if ent is not None \
                and (not config.DEVELOPMENT or ent.authProviders): 
            return ent # ok found it but if we are in dev - then we must have some test authProviders
            
        apTestList = []
        for i in ['facebook','twitter','google','instagram','linkedin','github']:
            apTestList.append( AuthProvider ( name   =i
                                            , id     =util.randomB64() 
                                            , secret_=util.randomB64() 
                                            ))  
        ent = cls (authProviders=apTestList)
        ent.key = key
        ent.put()
        return ent

        
    #def toDict(self, *args, **kwargs):
    def toDict(self, nullVals=False):
        """Creates dict representaion of config, recaptcha_forms are converted so angular models can
        easily use it"""        
        d = self.toDict_(publicOnly=False, nullprops=nullVals)
        d['development'] = config.DEVELOPMENT
        d['has_feedback']= bool(self.admin_email_)    
        return d

# coding: utf-8
"""Provides implementation of Config"""
from __future__ import absolute_import

from google.appengine.ext import ndb

import config
from model import ndbModelBase, ConfigAuth
import util
from pydash import _
import logging


class Config(ConfigAuth):
    """A class describing datastore config."""
    analytics_id        = ndb.StringProperty(default='')    # Google Analytics ID
    site_name           = ndb.StringProperty(default=config.APPLICATION_ID)  # Webapp name
    description         = ndb.StringProperty(default='')    # Webapp description
    admin_email_       = ndb.StringProperty(default='')    # private: Admin's email, where feedback will be sent
    flask_secret        = ndb.StringProperty(default=util.uuid())
    recaptcha_forms     = ndb.StringProperty(repeated=True) # List of form names where recaptcha is enabled
    recaptcha_secret    = ndb.StringProperty(default='')
    recaptcha_id        = ndb.StringProperty(default='')
    salt_              = ndb.StringProperty(default=util.uuid())
    verify_email        = ndb.BooleanProperty(default=True) # Whether to verify emails of newly registered users
    notify_on_new_user_= ndb.BooleanProperty(default=True) # Whether to send email to admin if user signs up

    # PUBLIC_PROPERTIES = ConfigAuth.get_public_properties() + \
                        # [ 'analytics_id'
                        # , 'site_name'
                        # , 'description'
                        # , 'recaptcha_id'
                       ##, 'has_recaptcha'
                        # , 'has_feedback_form'
                        # , 'recaptcha_forms'
                        # , 'verify_email'
                       ## todo if verify_email is public then why isnt this one:  'notify_on_new_user_' ?
                        # ]
    @property
    def has_feedback_form(self):
        """If feedback form should be displayed"""
        return bool(self.admin_email_)

    #@property
    def has_recaptcha(self):  # pylint: disable=missing-docstring
        return bool(self.recaptcha_secret) and bool(self.recaptcha_id)

    @classmethod
    def get_master_db(cls):
        """Get config entity doesn't exist, it creates new one.
        There's need only for one config - master"""
        return cls.get_or_insert('master')

    #def to_dict(self, *args, **kwargs):
    def to_dict(self, all=False):
        """Creates dict representaion of config, recaptcha_forms are converted so angular models can
        easily use it"""
        # p = self._properties.keys()
        # logging.debug('all properties')
        # for i in  p:
            # logging.debug('%r', i)
            
        # logging.debug('all = %r', all)
        # for i in  inc:
            # logging.debug('%r', i)
            
        #repr_dict = super(Config, self).to_dict(*args, **kwargs)
        d = self.toDict(all, all)
        #d['development'] = config.DEVELOPMENT
        
        #d['key'] = self.key.urlsafe() # todo why does client need these? 
        #d['id']  = self.key.id()      # todo why does client need these?
        #logging.debug('key = %r',d['key'])
        #logging.debug('id = %r',d['id'])
        
        # On clicking save at config page, get a 404 becasue <key> is somehow getting appended to url 
        # like this:       api/v1/config/<key> 
        # But When we comment out this:   d['key']= ...   then save config page works ok
        
        #todo 1) check whether and where client uses cfg.id or cfg.key
            # 2) check client need for  user private_properties  not just id and key
            # 3) replace sufixes  _p with _    and _h with __ 
            # 4) check property code cf dhammamap2
            # 5) minimise properties sent to client - more hidden and private - less nullprops=true
            # 6) finish converting old code
        
        
        if 'recaptcha_forms' in d:
            d['recaptcha_forms'] = util.list_to_dict(d['recaptcha_forms'])
        return d

    @classmethod
    def public_properties(cls):
        return  [ n for n in  cls.all_properties() 
                 if not (n.endswith('_') or n.endswith('_secret'))
                ]
    
    @classmethod
    def all_properties(cls):
        """Include the private ones but exclude the ndbModelBase properties('version', 'modified', 'created') before sending to client"""
        # all_properties = super(Config, cls).get_all_properties()
        # all_properties += cls.PUBLIC_PROPERTIES
        # return _.pull(_.uniq(all_properties), 'version', 'modified', 'created', 'key', 'id')
        
        # p1 = cls._properties
        # for i in p1:
            # logging.debug('*** %r', i)
            
        # p2 = util.decoratedProperties(cls)   
        # for i in p2:
            # logging.debug('=== %r', i)
            
       ## p1 = [n for n in p1 if not n.endswith('__')]
        # p3 = ndbModelBase._properties
        # for i in p3:
            # logging.debug('+++ %r', i)
            
        # p1 = [n for n in p1 if n not in p3]
        # for i in p1:
            # logging.debug('*** %r', i)
            
       # p1 += p2

        return [ n for n in  cls._properties.keys() 
                           + util.pyProperties(cls)
                 if n not in ndbModelBase._properties.keys()
               ]
        # for i in p:
            # logging.debug('xxx %r', i)
        # assert set(p1) == set(p)
        # return p

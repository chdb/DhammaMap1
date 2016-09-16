# coding: utf-8
"""Provides implementation of ndbModelBase """

from __future__ import absolute_import
from google.appengine.ext import ndb

import config
from datetime import date
#from pydash import _
import util
import logging

# class MyStringModel (ndb.Model):

# class MyStringProp (ndb.StringProperty):
    # readOnly = True
    # private = False
    # hidden = True
    
    # def _to_base_type(_s, v):
        # return v
        
    # def _from_base_type(_s, v):
        # return MyStringProp(v)
    
    # def __init__(_s, v):
        
  

class ndbModelBase(ndb.Model):
    """ndbModelBase model class, it should always be extended
    Attributes:
        created_r (ndb.DateTimeProperty)  : DateTime when model instance was created
        modified_r (ndb.DateTimeProperty) : DateTime when model instance was last time modified
        version_r (ndb.IntegerProperty)   : version of app
    """
    created_r = ndb.DateTimeProperty(auto_now_add=True)
    modified_r= ndb.DateTimeProperty(auto_now=True)
    version_r = ndb.IntegerProperty(default=config.CURRENT_VERSION_TIMESTAMP)
    
    def toDict_(_s, publicOnly, nullprops=False):
        """Return a dict containing the entity's property values, so it can be passed to client
        Args:		include (list, optional): Set of property names to include, default all properties
        """
        suffix = '_' if publicOnly else '__'
              
        d = util.deepFilter ( _s.to_dict()
                            , lambda k,v: not k.endswith(suffix)
                                          and (v or nullprops or isinstance(v, bool))   # unless nullprops or boolean, exclude items with falsy values EG '' or None
                            , lambda k,v: v.isoformat() if isinstance(v, date) else v   # convert date type values to a string repr
                            )
         
        # logging.debug('base toDict xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        # for k,v in  d.iteritems():
            # logging.debug('%r\t\t%r', k,v)
        # logging.debug(' 0 xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
 
        return d

    def populate(_s, ka):
        """Extended ndb.Model populate method, so it can ignore properties, which are not defined in model class without throwing error
        """
        #todo add publicOnly param - if true  and client has tried to modify private prop. throw 403
        
        # logging.debug('before +++++++++++++++++++++++++++++++++++')
        # for k,v in ka.iteritems():
            # logging.debug('%r\t\t%r', k,v)
        
        # logging.debug('properties +++++++++++++++++++++++++++++++++++')
        # for i in _s._properties:
            # logging.debug('%r', i)
        
        ka = {k:v for k,v in ka.iteritems() if k in _s._properties} # remove extra properties at  root level
        ka = util.deepFilter (ka, lambda k,v : not k.endswith('_r')) # exclude read-only properties at all levels

        # logging.debug('after +++++++++++++++++++++++++++++++++++')
        # for k,v in ka.iteritems():
            # logging.debug('%r\t\t%r', k,v)
        # logging.debug('+++++++++++++++++++++++++++++++++++++++++++')
     
        super(ndbModelBase, _s).populate(**ka)

    @classmethod
    def get_by(cls, name, value):
        """Gets model instance by given property-name and value"""
        return cls.query(getattr(cls, name) == value).get()

    # @classmethod
    # def get_public_properties(cls):
        # """Public properties consist of this class public properties plus extending class public properties"""
        # return cls.PUBLIC_PROPERTIES + ndbModelBase.PUBLIC_PROPERTIES

    # @classmethod
    # def public_properties(cls):
        # return [ n for n in  cls.all_properties() 
                 # if not (  n.endswith('_') 
                        # or n.endswith('_secret'))
               # ]

    # @classmethod
    # def all_properties(cls):
        # return [ n for n in   cls._properties.keys() 
                            # + util.pyProperties(cls)  # todo review whether we want to include these
                 # if not n.endswith('__') 
               # ]

    # @classmethod
    # def get_private_properties(cls):
        # """Gets private properties defined by extending class"""
        # return cls.PRIVATE_PROPERTIES + ndbModelBase.PRIVATE_PROPERTIES + cls.get_public_properties()

    # @classmethod
    # def get_all_properties(cls):
        # """Gets all model's ndb properties"""
        # return ['key'] + _.keys(cls._properties)



# coding: utf-8
"""Provides implementation of ndbModelBase """

from __future__ import absolute_import
from google.appengine.ext import ndb

#import config
from datetime import date
import util
from env import ENV
import logging  

class ndbModelBase(ndb.Model):
    """
    Properties of ndbModelBase and subclasses can have the following suffixes which server code will 
    use to govern client behaviour.The sufffixes subdivide model properties into 4 groups 
        _r      : readonly - visible but not to be modified by client
        __      : hidden - not visible (and not sent) to any client
        _       : private - visible only to privileged clients (administrators)
        (none)  : public - the attribute is visible and modifiable
    """
    created_r  = ndb.DateTimeProperty(auto_now_add=True)         # when model instance was created
    modified_r = ndb.DateTimeProperty(auto_now=True)             # when model instance was last modified
    version_r  = ndb.IntegerProperty (default=ENV['CURRENT_VERSION_TIMESTAMP']) # app version number 
    
    def toDict_(_s, publicOnly, nullprops=False):
        """Return a dict containing the entity's property values, to be passed to client
        publicOnly:	true excludes hidden and private properties
                    false includes private but not hidden properties
        nullProps:  whether to include properties with value None (useful if client need property names)
        """
        suffix = '_' if publicOnly else '__'
              
        data, filtrate = util.deepFilter ( _s.to_dict() # defined in ndb.Model 
            , lambda k,v: not k.endswith(suffix)
                          and (v or nullprops or isinstance(v, bool))   # unless nullprops or boolean, exclude items with falsy values EG '' or None
            , lambda k,v: v.isoformat() if isinstance(v, date) else v   # convert date type values to a string repr
            )
        util.debugDict(filtrate, 'filtered out these:')
        return data

    def populate(_s, ka):
        """Extended ndb.Model populate method, so it can ignore properties, which are not defined in model class without throwing error
        """
        #todo add publicOnly param - if true  and client has tried to modify private prop. throw 403

        util.debugDict(ka, 'populating: ')
        
        ka.pop('_k',None)
        bad = [k for k in ka if k not in _s._properties]
        if bad:
            logging.warning ('Invalid update: contains unknown field: %r', bad)
            raise ValueError('Invalid update')
        
        bad = util.deepFindKey(ka, lambda k: k.endswith('_r'))
        if bad:
           # logging.warning ('Invalid update: contains read-only fields: %r', bad)
            raise ValueError('Invalid update: contains read-only fields: %r'% bad)
            
#        ka = {k:v for k,v in ka.iteritems() if k in _s._properties} # remove extra properties at  root level
#        ka = util.deepFilter (ka, lambda k,v : not k.endswith('_r')) # exclude read-only properties at all levels
     
        #util.debugDict(ka, 'wwwwwwwwwwww')
        super(ndbModelBase, _s).populate(**ka)

    @classmethod
    def get_by(cls, propName, value):
        #todo replace with indexing - or use ndb key for unique value
        """Gets model instance by given property-name and value"""
        return cls.query(getattr(cls, propName) == value).get()


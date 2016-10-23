# coding: utf-8
"""Provides implementation of ndbModelBase """

from __future__ import absolute_import
from google.appengine.ext import ndb

import config
from datetime import date
import util
import logging  

class ndbModelBase(ndb.Model):
    """ndbModelBase model class, it should always be extended
    Attributes:
        created_r (ndb.DateTimeProperty)  : DateTime when model instance was created
        modified_r (ndb.DateTimeProperty) : DateTime when model instance was last time modified
        version_r (ndb.IntegerProperty)   : version of app
    """
    created_r = ndb.DateTimeProperty(auto_now_add=True)
    modified_r= ndb.DateTimeProperty(auto_now=True)
    version_r = ndb.IntegerProperty (default=util.VERtimeStamp)
    
    def toDict_(_s, publicOnly, nullprops=False):
        """Return a dict containing the entity's property values, so it can be passed to client
        Args:		include (list, optional): Set of property names to include, default all properties
        """
        suffix = '_' if publicOnly else '__'
              
        data, filtrate = util.deepFilter ( _s.to_dict() 
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
            logging.warning ('Invalid update: contains read-only fields: %r', bad)
            raise ValueError('Invalid update')
            
#        ka = {k:v for k,v in ka.iteritems() if k in _s._properties} # remove extra properties at  root level
#        ka = util.deepFilter (ka, lambda k,v : not k.endswith('_r')) # exclude read-only properties at all levels
     
        #util.debugDict(ka, 'wwwwwwwwwwww')
        super(ndbModelBase, _s).populate(**ka)

    @classmethod
    def get_by(cls, propName, value):
        #todo replace with indexing - or use ndb key for unique value
        """Gets model instance by given property-name and value"""
        return cls.query(getattr(cls, propName) == value).get()


# coding: utf-8
"""Provides implementation of ndbModelBase and Validator"""

from __future__ import absolute_import
from google.appengine.ext import ndb

import config
from datetime import date
from pydash import _
import util
import logging


class Validator(object):
    """Base factory class for creating validators for ndb properties
    To create a validator for some property, its model class defines a rule in the form of a class attribute with one of these types:
        list        - with 2 elements, determining min and max length of string
        regex       - which will be validated against string
        function    - custom validation function
    For example:
        class MySuperValidator (Validator):
            short_name_rule = [2, 4]
    Now the call 
        MySuperValidator.create('short_name_rule') 
    returns a function which will throw an error if a string is not between 2-4 chars.
    Similarly if short_name_rule was a regex, or if it was a function, the appropriate function is returned as validator
    This is useful for passing a 'validator' argument to ndb.Property constructor and also passing a 'type'
    argument to reqparse.RequestParser, when adding argument via add_argument.
    """
    @classmethod
    def fn(cls, name, required=True): # NB  'required' defaults to True  for our base.Validator().fn()
                                      # but 'required' defaults to False for reqparse.RequestParser().add_argument()
        """Creates validation function for given attribute name
        Args:		name (string): Name of attribute
                    required (bool, optional) If false, empty string will be valid
        Returns:	function    : validation function
        """
        def create_validator(required, lengths=None, regex=None):
            """Factory function to create a validator function according to lengths or regex
            Args:		lengths (list)  : list of length 2. e.g [3, 7] indicating that 
                                            string should be between 3 and 7 characters
                        regex (string)  : Regular expression
                        required (bool) : Whether empty value '' should be accepted as valid, ignoring other constraints
            Returns:	function        : Function, which will be used for validating input
            """
            assert (lengths is None) or (regex is None)
        
            def validator_function(value, prop):
                """Function validates input against constraints given from closure function
                These functions are primarily used as ndb.Property validators
                Args:		value (string)  : input value to be validated
                            prop (string)   : ndb.Property name, which is validated
                Returns:	string          : Returns original string, if valid
                Raises:		ValueError      : If input isn't valid
                """
                # NB For compatibility with Flask's RequestParser type conversion we have this arg order (vslue,prop)
                if isinstance(value, ndb.Property):     # ...But ndb.validator args are the other way round IE (prop,value)
                    value = prop            # ...so if the "value" is a ndb.Property, then the "prop" is really the value 
                
                if not required and value == '':
                    return ''
                if regex:
                    return util.match_regex(value, regex)
                return util.limit_string(value, lengths[0], lengths[1])

            return validator_function

        attr = getattr(cls, name)
        if _.is_list(attr):
            return create_validator(required, lengths=attr)
        if _.is_string(attr):
            return create_validator(required, regex=attr)
        if _.is_function(attr):
            return attr

    @classmethod
    def toDict(cls):
        """Creates dict out of list and regex attributes, so it can be passed to angular for frontend validation
            Returns:		dict:
        """
        result = {}
        for attr_name in _.reject(set(dir(cls)), lambda x: x.startswith('_')):
            attr = getattr(cls, attr_name)
            if _.is_list(attr) or _.is_string(attr):
                result[attr_name] = attr
        return result


class ndbModelBase(ndb.Model):
    """ndbModelBase model class, it should always be extended
    Attributes:
        created (ndb.DateTimeProperty)  : DateTime when model instance was created
        modified (ndb.DateTimeProperty) : DateTime when model instance was last time modified
        version (ndb.IntegerProperty)   : Version of app
        PUBLIC_PROPERTIES (list)        : list of properties, which are accessible for public, meaning non-logged users. 
                                            Every extending class should define public properties, if there are some
        PRIVATE_PROPERTIES (list)       : list of properties accessible by admin or other authorized user
    """
    created     = ndb.DateTimeProperty(auto_now_add=True)
    modified    = ndb.DateTimeProperty(auto_now=True)
    version     = ndb.IntegerProperty(default=config.CURRENT_VERSION_TIMESTAMP)

    #PUBLIC_PROPERTIES = ['key', 'version', 'created', 'modified']
   # PRIVATE_PROPERTIES = []

    def toDict_(self, all, nullprops=False):
        """Return a dict containing the entity's property values, so it can be passed to client
        Args:		include (list, optional): Set of property names to include, default all properties
        """
        '''Todo: refactor ndbModelBase.toDict() 
                          ndbModelBase.PUBLIC_PROPERTIES
                          ndbModelBase.PRIVATE_PROPERTIES
                          ndbModelBase.get_public_properties
                          ndbmodel.get_private_properties
                          Config  .get_all_properties
                          Config  .get_private_properties
                          User    .get_public_properties
                          User    .get_private_properties
        Some properties are added removed explicitly from eg PUBLIC_PROPERTIES - eg  Config.get_all_properties
        this is all unecessarily complex. 
        There are only these 4 call types in the codebase
            user     .toDict(include=User  .get_public_properties()) # 2 calls: user_api.py*2
            user     .toDict(include=User  .get_private_properties())# 4 calls: auth_api.py*3 index.py
            CONFIG_DB.toDict(include=Config.get_public_properties()) # 2 calls: auth_api.py   index.py
            CONFIG_DB.toDict(include=Config.get_all_properties())    # 2 call: config_api.py  index.py
        So we could replace these with these 4
            user     .public_dict() 
            user     .private_dict()
            CONFIG_DB.public_dict() 
            CONFIG_DB.full_dict()  -where full = public + private ???
        
        NB ArgVdr's have another toDict() and more manual property lists which is no better
        '''
        include = self.all_properties() if all else self.public_properties()
        logging.debug('toDict for %r',include)
        d = {}
        if include is None:
            return super(ndbModelBase, self).toDict(include=include)

        for name in include:
            attr = getattr(self, name)
            # if name == 'key':
                # repr_dict[name] = self.key.urlsafe()
                # repr_dict['id'] = self.key.id()
            # el
            if isinstance(attr, date):
                d[name] = attr.isoformat() # convert date type to string repr
            elif attr or nullprops or isinstance(attr, bool):
                d[name] = attr  # unless nullprops or boolean, exclude items with 'null' ie falsy values EG '' or None
     
        #logging.debug('toDict: %r', d)
        return d

    def populate(self, **ka):
        """Extended ndb.Model populate method, so it can ignore properties, which are not defined in model class without throwing error
        """
        ka = _.omit(ka, ndbModelBase.public_properties() )  # We don't want to populate those properties
        assert 'key' not in ka
        assert 'id'  not in ka
        ka = _.pick(ka, _.keys(self._properties))  # We want to populate only real model properties
        super(ndbModelBase, self).populate(**ka)

    @classmethod
    def get_by(cls, name, value):
        """Gets model instance by given property name and value"""
        return cls.query(getattr(cls, name) == value).get()

    # @classmethod
    # def get_public_properties(cls):
        # """Public properties consist of this class public properties plus extending class public properties"""
        # return cls.PUBLIC_PROPERTIES + ndbModelBase.PUBLIC_PROPERTIES

    @classmethod
    def public_properties(cls):
        return [ n for n in  cls.all_properties() 
                 if not (  n.endswith('_') 
                        or n.endswith('_secret'))
               ]

    @classmethod
    def all_properties(cls):
        return [ n for n in   cls._properties.keys() 
                            + util.pyProperties(cls)  # todo review whether we want to include these
                 if not n.endswith('__') 
               ]

    # @classmethod
    # def get_private_properties(cls):
        # """Gets private properties defined by extending class"""
        # return cls.PRIVATE_PROPERTIES + ndbModelBase.PRIVATE_PROPERTIES + cls.get_public_properties()

    # @classmethod
    # def get_all_properties(cls):
        # """Gets all model's ndb properties"""
        # return ['key'] + _.keys(cls._properties)



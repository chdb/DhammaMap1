# coding: utf-8
"""Provides implementation of Base model and BaseValidator"""

from __future__ import absolute_import
from google.appengine.ext import ndb

import config
from datetime import date
from pydash import _
import util


class BaseValidator(object):
    """Base factory class for creating validators for ndb properties
    To create a validator for some property, its model class defines a rule in the form of a class attribute with one of these types:
        list        - with 2 elements, determining min and max length of string
        regex       - which will be validated against string
        function    - custom validation function
    For example:
        class MySuperValidator (BaseValidator):
            short_name_rule = [2, 4]
    Now the call 
        MySuperValidator.create('short_name_rule') 
    returns a function which will throw an error if a string is not between 2-4 chars.
    Similarly if short_name_rule was a regex, or if it was a function, the appropriate function is returned as validator
    This is useful for passing a 'validator' argument to ndb.Property constructor and also passing a 'type'
    argument to reqparse.RequestParser, when adding argument via add_argument.
    """
    @classmethod
    def create(cls, name, required=True):
        """Creates validation function from given attribute name
        Args:		name (string): Name of attribute
                    required (bool, optional) If false, empty string will be always accepted as valid
        Returns:	function    : validation function
        """
        def create_validator(lengths=None, regex='', required=True):
            """This is factory function, which creates validator functions, which
            will then validate passed strings according to lengths or regex set at creation time
            Args:		lengths (list)  : list of length 2. e.g [3, 7] indicating that 
                                            string should be between 3 and 7 characters
                        regex (string)  : Regular expression
                        required (bool) : Whether empty value '' should be accepted as valid, ignoring other constraints
            Returns:	function        : Function, which will be used for validating input
            """
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
            return create_validator(lengths=attr, required=required)
        if _.is_string(attr):
            return create_validator(regex=attr, required=required)
        if _.is_function(attr):
            return attr

    @classmethod
    def to_dict(cls):
        """Creates dict out of list and regex attributes, so it can be passed to angular for frontend validation
            Returns:		dict:
        """
        result = {}
        for attr_name in _.reject(set(dir(cls)), lambda x: x.startswith('_')):
            attr = getattr(cls, attr_name)
            if _.is_list(attr) or _.is_string(attr):
                result[attr_name] = attr
        return result


class Base(ndb.Model):
    """Base model class, it should always be extended
    Attributes:
        created (ndb.DateTimeProperty)  : DateTime when model instance was created
        modified (ndb.DateTimeProperty) : DateTime when model instance was last time modified
        version (ndb.IntegerProperty)   : Version of app
        PUBLIC_PROPERTIES (list)        : list of properties, which are accessible for public, meaning non-logged users. 
                                            Every extending class should define public properties, if there are some
        PRIVATE_PROPERTIES (list)       : list of properties accessible by admin or authrorized user
    """
    created     = ndb.DateTimeProperty(auto_now_add=True)
    modified    = ndb.DateTimeProperty(auto_now=True)
    version     = ndb.IntegerProperty(default=config.CURRENT_VERSION_TIMESTAMP)

    PUBLIC_PROPERTIES = ['key', 'version', 'created', 'modified']
    PRIVATE_PROPERTIES = []

    def to_dict(    self, include=None):
        """Return a dict containing the entity's property values, so it can be passed to client
        Args:		include (list, optional): Set of property names to include, default all properties
        """
        repr_dict = {}
        if include is None:
            return super(Base, self).to_dict(include=include)

        for name in include:
            attr = getattr(self, name)
            if isinstance(attr, date):
                repr_dict[name] = attr.isoformat()
            elif isinstance(attr, ndb.Key):
                repr_dict[name] = self.key.urlsafe()
                repr_dict['id'] = self.key.id()
            else:
                repr_dict[name] = attr

        return repr_dict

    def populate(self, **kwargs):
        """Extended ndb.Model populate method, so it can ignore properties, which are not defined in model class without throwing error
        """
        kwargs = _.omit(kwargs, Base.PUBLIC_PROPERTIES + ['key', 'id'])  # We don't want to populate those properties
        kwargs = _.pick(kwargs, _.keys(self._properties))  # We want to populate only real model properties
        super(Base, self).populate(**kwargs)

    @classmethod
    def get_by(cls, name, value):
        """Gets model instance by given property name and value"""
        return cls.query(getattr(cls, name) == value).get()

    @classmethod
    def get_public_properties(cls):
        """Public properties consist of this class public properties plus extending class public properties"""
        return cls.PUBLIC_PROPERTIES + Base.PUBLIC_PROPERTIES

    @classmethod
    def get_private_properties(cls):
        """Gets private properties defined by extending class"""
        return cls.PRIVATE_PROPERTIES + Base.PRIVATE_PROPERTIES + cls.get_public_properties()

    @classmethod
    def get_all_properties(cls):
        """Gets all model's ndb properties"""
        return ['key', 'id'] + _.keys(cls._properties)



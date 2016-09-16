# coding: utf-8

from __future__ import absolute_import #todo shouldn't we have this on every module or on none?
import logging
from google.appengine.ext import ndb #pylint: disable=import-error
from google.appengine.datastore import datastore_query#.Cursor #pylint: disable=import-error
import re
        
def fn(vp, required=True): # vp :- validator parameter

    def validator(required, lengths=None, regex=None):
        assert (lengths is None) or (regex is None)
    
        def validator_function(value, prop):
            if isinstance(value, ndb.Property): # ...But ndb.validator args are the other way round IE (name,value)
                value = prop                    # ...so if the "value" is a ndb.Property, then the "prop" is really the value 
            
            if not required and value == '':
                return ''
            if regex:
                return match_regex(value, regex)
            return limit_string(value, lengths[0], lengths[1])

        return validator_function

    #attr = getattr(cls, name)
    if isinstance(vp, list):
        return validator(required, lengths=vp)
    if isinstance(vp, basestring):
        return validator(required, regex=vp)
 #   assert vp.__name__.endswith('Vdr'), 'Names of all custom Validators must have "Vdr" suffix.'
    assert callable(vp)
    return vp # custom validator


    @classmethod
    def toDict(cls):
        """Creates dict out of list and regex attributes, so it can be passed to angular for frontend validation
            Returns:		dict:
        """
        # result = {}
        # for attr_name in _.reject(set(dir(cls)), lambda x: x.startswith('_')):
            # attr = getattr(cls, attr_name)
            # if _.is_list(attr) or _.is_string(attr):
                # result[attr_name] = attr
        
        # logging.debug('vdrs toDict xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        # for k,v in  result.iteritems():
            # logging.debug('%r\t\t%r', k,v)
        # logging.debug(' v xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
                
        result = { k:v for k,v in cls.__dict__.iteritems() 
                   if not(k.startswith('_') or k.endswith('Vdr')) }
        
        # logging.debug('vdrs2 toDict xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        # for k,v in  result.iteritems():
            # logging.debug('%r\t\t%r', k,v)
        # logging.debug(' v2 xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        return result

#@staticmethod
def limit_string(string, minlen, maxlen):
    """Validation function constrains minimal and maximal lengths of string.
    Args:		string (string) : String to be checked
                minlen (int)    : Minimal length
                maxlen (int)    : Maximal length
    Returns:	string          : Returns given string
    Raises:	    ValueError      : If string len is out of range
    """
    assert minlen >= 0
    assert maxlen >= 0
    assert maxlen == 0 or maxlen > minlen
    
    n = len(string) 
    if n < minlen:
        raise ValueError('At least %s characters long' % minlen)
    if maxlen > 0:
        if n > maxlen:
            raise ValueError('Maximum of %s characters long' % maxlen)
    return string

#@staticmethod
def match_regex(string, regex):
    """Validation function checks validity of string for given regex.
    Args:		string (string) : String to be checked
                regex (string)  : Regular expression
    Returns:	string          : Returns given string
    Raises:		ValueError      : If string doesn't match regex
    """
    h = re.compile(regex, re.IGNORECASE)        # todo store h in g or app.registry ?
    if not h.match(string):
        raise ValueError('Incorrect regex format')
    return string

##################################################################################
######## Validators ##############################################################
#class ArgVdr(Validator):
    # """This validator class contains validators in the form of attributes and methods, for user input which
    # is not associated with any particular datastore model, but still needs to be validated
    # """
feedback_span = [1, 2000] #determining min and max lengths of feedback message sent to admin

def captchaVdr (captchaStr):
    """Verifies captcha by sending it to google servers
    Args    : captchaStr (string): captcha string received from client.
    Raises  : ValueError: If captcha is incorrect
    """
    # todo: this code does not seem right - register to get keys, test and rewrite?
    
    if config.CONFIG_DB.has_recaptcha():
        params = { 'secret'  : config.CONFIG_DB.recaptcha_secret
                 , 'remoteip': request.remote_addr
                 , 'response': captchaStr
                 }
        params = urllib.urlencode(params)
        result = urlfetch.fetch( url='https://www.google.com/recaptcha/api/siteverify'
                               , payload=params
                               , method=urlfetch.POST
                               , headers={'Content-Type': 'application/x-www-form-urlencoded'}
                               )
        success = json.loads(result.content)['success']
        if not success:
            raise ValueError('Sorry, invalid captcha')
    return captchaStr

def cursorVdr (cursor):
    """Verifies if given string is valid ndb query cursor, if so returns instance of it
    Args    : cursor (string): Url encoded ndb query cursor
    Returns : google.appengine.datastore.datastore_query.Cursor: ndb query cursor
    Raises  : ValueError: If cursor fails
    """
    #logging.debug('xxxxxxxxx cursor = %r',cursor)
    if not cursor:
        return None
    try:
        cursorObj = datastore_query.Cursor(urlsafe=cursor)
    except:
        logging.exception('cursor string failed in validator')
        raise ValueError('Sorry, invalid cursor.')
    return cursorObj


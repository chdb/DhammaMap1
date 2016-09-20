# coding: utf-8

from __future__ import absolute_import #todo shouldn't we have this on every module or on none?
import logging
from google.appengine.ext import ndb #pylint: disable=import-error
from google.appengine.datastore import datastore_query#.Cursor #pylint: disable=import-error
import re
import config
        

def limit_string(string, ls2):
    """impose minimal and maximal lengths of string.
    NB maxlen = 0 indicate there is no max length  (not that the max is zero)
    """
    assert len(ls2) == 2 ,'specifier v should be a 2 member list'
    minlen = ls2[0]
    maxlen = ls2[1]
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


def match_regex(string, regex):
    """checks validity of string for given regex.
    """
    h = re.compile(regex, re.IGNORECASE)        # todo store h in g or app.registry ?
    if not h.match(string):
        raise ValueError('Incorrect regex format')
    return string

    
class Vdr(object):     

    def init (_s, spec, fn):
        def validator (arg1, arg2):                   
            # For ndb property the validator signature is:  value = validator (property, value)   but in requestParser.add_argument() 
            # the 'type' param expects this signature:      value = typeFn    (value [, otherArgs] )  This is the other way round for value arg (we dont use the other args
            value = arg2 if isinstance(arg1, ndb.Property) else arg1  
            
            # if not required and value == '':  #todo delete - We dont need required param do we?
                # return ''
            return fn(value, spec)
        
        _s.fn = validator
        _s.specifier = spec
     
class regexVdr(Vdr):   
    def __init__(_s, spec):  _s.init(spec, match_regex)
        
class lengthVdr(Vdr):   
    def __init__(_s, spec):  _s.init(spec, limit_string)
    
    
def to_dict(module):
    # return dict of validator-specifiers in given module 
    # IE all module level items wit the suffixes as below
    return  { k : getattr(module, k).specifier for k in dir(module) 
                if k.endswith('_span')  # lengthVdr.specifier
                or k.endswith('_rx')    # regexVdr.specifier
            }    


######## Specified Validators ##############################################################

feedback_span = lengthVdr([1,2000]) #determining min and max lengths of feedback message sent to admin

# User ####################
name_span     = lengthVdr([0,100])
username_span = lengthVdr([3, 40])
password_span = lengthVdr([6, 70])
bio_span      = lengthVdr([0,140])
location_span = lengthVdr([0, 70])
social_span   = lengthVdr([0, 50])

email_rx  = regexVdr(config.EmailRegEx)

######## Custom Validators ##############################################################

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

##################################################################################

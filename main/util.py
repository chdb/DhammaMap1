# coding: utf-8
"""
Set of utility function used throughout the app
"""
#import config
import os
import base64
import logging
import time as tim
from datetime import datetime

# The conde in index.py sends this serverside email regex to clientside along with other validators 
# Note that currently, email fields on clientside forms dont use it.  Instead they will use the regex provided by AngularJS
#var EMAIL_REGEXP = /^[a-z0-9!#$%&'*+\/=?^_`{|}~.-]+@[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*$/i;
#  python str =    r'^[a-z0-9!#$%&\'*+\/=?^_`{|}~.-]+@[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*$'
# This is broadly similar except for allowing the domain-part to be just a single TLD   eg joebloggs@com    
# it is also lowercase only for use with a case-insensitive search
#and does not allow domain part to start with '-'
def getEmailRegex():   
    #Use as a pre-validator, to be followed by proper live validation by mailgun service 
    #Note that it is currently too strict a) does not allow new forms i18n email addresses. And b) weird and outdated forms that are permissed by the RFC and possibly by some mail servers  
    EMAIL_REGEX =  r'^[a-z0-9-!#$%&\'*+\/=?^_`{|}~.]+@[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*$'
    
    def findNgEMAIL_REGEXP():
        '''Find and return the email regex in AngularJS code. If not found return None
        Of course both sides need to follow the same rules so index.py sends our regex email validator to clientside with .
        But this is the wrong round because as new versions get installed, AngularJs is likely to be more up to date
        Therefore we use this function to get the regex from AngularJS, assuming it has the same name in the same file in the code
        And clientside does not even use the one we send. It uses the one provided by AngularJS.)
        '''
        curdir = os.path.dirname(__file__)
        logging.debug('cur dir: %s',curdir)
        ngpath = os.path.join(curdir, r'public\lib\angular\angular.js')
        logging.debug('ngpath: %s',ngpath)

        found = None
        start = 'var EMAIL_REGEXP = /'
        end = '/i;\n'
        with open(ngpath, 'rU') as fp:
            for line in fp:
                if  line.startswith(start)\
                and line.endswith(end):
                    logging.debug('line: %s',line)
                    found = line
                    break
        if found:
            ngEMAIL_REGEXP = found[len(start):-len(end)]
            logging.debug('regex: %s', ngEMAIL_REGEXP)
            return ngEMAIL_REGEXP
        
        logging.warning ('email regex line not found in AngularJS code')
        return None
        
    # return AngularJS email regex, or our own one, if not found.    
    return findNgEMAIL_REGEXP() or EMAIL_REGEX

# class Config (object):
DEVT = not os.environ.get('SERVER_SOFTWARE', '').startswith('Google App Eng')
VERid = os.environ.get('CURRENT_VERSION_ID')
VERname = VERid.split('.')[0]

if DEVT:
    import calendar
    VERtimeStamp = calendar.timegm(datetime.utcnow().timetuple())
else:
    VERtimeStamp = long(VERid.split('.')[1]) >> 28
logging.debug('####################################################### cur ver id: %r'      , VERid)
logging.debug('####################################################### cur ver name: %r'    , VERname)
logging.debug('####################################################### cur ver timestamp: %r',VERtimeStamp)
logging.debug('####################################################### cur ver datetime: %r', datetime.utcfromtimestamp(VERtimeStamp))

# def ConfigFactory(_x = Config() ) : return _x
    
#def uuid():
    # """Generates random UUID used as user token for verification, reseting password etc.
    # Returns:	string:     32 characters long 
    # """
    #return uuid4().hex

#todo provide a raw token - they will be b64-encoded again 
#because the token is part of the Kryptoken 
def randomB64(n=15):
    '''a base64 string representing n random bytes (so string has length = ceil(n/3)*4 )
       Is 15 enough to create a good nonce?  - should be plenty eg if we just want to avoid a clash on same machine '''
    #n = config('NonceBytes')
    r = os.urandom(n) 
    #return os.urandom(8) 
    #todo Do we need to base64-encode? Surely the token will be wrappped in a crytoken which will do it?
    return base64.urlsafe_b64encode(r)


def create_name_from_email(email):
    """Function tries to recreate real name from email address
    Examples:     >>> create_name_from_email('bobby.tables@email.com')
                  Bobby Tables
                  >>> create_name_from_email('bobby-tables@email.com')
                  Bobby Tables
    Args:		email (string)  : Email address
    Returns:	string          : Hopefully user's real name
    """
    local_part =  email.split('@')[0]
    separator = r'_+|-+|\.+|\++' # regex for one of these 4 chars _ - . + (optionally repeated)  
    return re.sub(separator, ' ', local_part).title()


def sNow():
    return int(tim.time()) # seconds since epoch.  time() returns float with system-dependent resolution - some only resolve to nearest second

def msNow():
    return int(tim.time()*1000) # milliSeconds since epoch.  

# def dsNow():
    # return int(tim.time()*10) # deciSeconds since epoch.  


# def list_to_dict(input_list):
    # """Creates dictionary with keys from list values
    # This function is useful for converting passed data from Angular group of checkboxes  eg named (a, b, c, d),
    # since angular ng-model doesn't deliver a list of just the checked ones in the group, eg (b,d) instead
    # it returns something like {'a': False, 'b': True, 'c': False, 'd': True} for the group
    # Example:        >>> list_to_dict(['a', 'b'])
                    # {'a': True, 'b': True}
    # Args:		input_list (list)   : List of any type
    # Returns:	dict                : Dict with 'True' values
    # """
    # return _.zip_object(input_list, _.map(input_list, _.constant(True)))


# def dict_to_list(input_dict):
    # """Creates list from dictionary with true booloean values
    # This function is primarily useful for converting passed data from Angular checkboxes,
     # since angular ng-model can't return list of checked group of checkboxes, instead
     # it returns something like {'a': True, 'b': True} for each checkbox
    # Example:        >>> dict_to_list({'a': True, 'b': True, 'c': False})
                    # ['a', 'b']
    # Args:		input_dict (dict): Dict with boolean values
    # Returns:	list: list of truthful values
    # """
    # return _.keys(_.pick(input_dict, _.identity))

        
# def filterDictListDict(d, filter):
    # ''' For a dict d and string s,  return a dict having removed all items with key ending with s 
        # If a value of d is a list of dicts, this will also filter those subkeys ending with s.
        # This uses a dictionary comprehension            { k1:v1 for ... }
             # with optional nested list comprehension    [ i for ... ]
        # with optional nested dictionary comprehension   { k2:v2 for ...}
    # '''
    # return { k1:[   {   k2:v2
                        # for k2,v2 in i.iteritems() 
                        # if filter(k2,v2) #not k2.endswith(s)
                    # } if isinstance(i, dict) else i
                    # for i in v1
                # ] if isinstance(v1, list) else v1             
             # for k1,v1 in d.iteritems() 
             # if filter(k1,v1) #not k1.endswith(s)
           # }
# todo replace with full recursion on all iterables  - use hasattr('__iter__') and filter by function param


# def deepFilter (c, filterFn):
    # if isinstance (c, dict):
        # return {k: deepFilter(v, filterFn) for k,v in c.iteritems() if filterFn(k,v) }
    # if isinstance (c, list):
        # return [deepFilter(i, filterFn) for i in c]
    # return c
    
    
def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n-1) + fib(n-2)

memo = {0:0, 1:1}
def fibm(n):
    if not n in memo:
        memo[n] = fibm(n-1) + fibm(n-2)
    return memo[n]

def deepFilter (c, filterFn, updateFn=None):
    '''c is a json object - ie consisting of elements of type string, number, bool or None in nested lists and dicts.
    deepFilter() returns the result of recursively applying the filter and update functions to all dicts in c, 
    to remove or update dict members.
    filterFn(k,v) is a predicate (ie boolean function) returning True to include (k:v)   It must not modify k or v.
    updateFn(k,v) is a modifying function for dict values. It returns updated or same v.  
    '''
    if updateFn is None:
        updateFn = lambda k,v: v
   
    filtrate = {}
    def deepFilter_ (c):
        if isinstance (c, dict):
            filtrate.update ({ k : v 
                     for k,v in c.iteritems() 
                     if not filterFn(k,v) 
                   })
            return { k : deepFilter_(updateFn(k,v)) 
                     for k,v in c.iteritems() 
                     if filterFn(k,v) 
                   }
        if isinstance (c, list):
            return [ deepFilter_(i) for i in c ]
        return c
        
    return deepFilter_ (c), filtrate

def deepFindKey (c, pred):
    """ depth-first search of c, a json object consisting of nestedlists and dicts, 
        returns the all dict keys (at whatever level) satisfying the predicate pred.
    """
    def _deepFindKey (c, pred):
        if isinstance(c, dict):
            for k,v in c.iteritems():
                if pred(k):
                    res.append(k)
                _deepFindKey(v, pred)
        elif isinstance(c, list):
            for i in c:
                _deepFindKey(i, pred)   
                
    res = []
    _deepFindKey (c, pred)
    return res
         
    
def pyProperties(cls):
    '''return a list of names of all the python properties in cls
    NB Normally properties are created with the @property decorator, 
    but they can also be created using property() built-in function, and in other arcane ways. 
    '''
    return [k for k, v in vars(cls).items() if isinstance(v, property)]

def debugList (lst, label):
    logging.debug('%s +++++++++++++++++++++++++++++++++++', label)
    if lst and hasattr(lst,'__iter__'):
        for i in lst:
            logging.debug('%r', i)
    else:
        logging.debug('%r', lst)
    logging.debug('+++++++++++++++++++++++++++++++++++++++++++')

def debugDict (d, label):
    logging.debug('%s +++++++++++++++++++++++++++++++++++', label)
    if d and hasattr(d,'iteritems'):
        for k,v in d.iteritems():
            logging.debug('%r \t: %r', k,v)
    else:
        logging.debug('%r', d)
    logging.debug('+++++++++++++++++++++++++++++++++++++++++++')

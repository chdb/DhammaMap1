# coding: utf-8
"""
Set of utility function used throughout the app
"""
from uuid import uuid4
import hashlib
import re
from google.appengine.ext import ndb #pylint: disable=import-error
import config
from pydash import _
import os
import logging


def getEmailRegex():   
    #todo: this is both too strict and too lenient. Replace it with a good but lenient rx.  Use as a pre-validator, to be followed by proper live validation by mailgun service 
    #  
    EMAIL_REGEX      =  r'^[a-z0-9-!#$%&\'*+\/=?^_`{|}~.]+@[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*$'
    #EMAIL_REGEX      = r'^[a-z0-9-!#$%&\'*+\.\/=?^_`{|}~]+@([-0-9a-z]+\.)+([0-9a-z]){2,}$'
    #email address  :=                          <local-part>  @  <domain-part>
    #domain-part    :=                                           <d-labels>      <top-level-domain>
    #local-part     :=                     <local-part-char> +
    #local-part-char:=    [-!#$%& '*+ \. /   =?      ^_`{|}~]                                       ## literals
    #                     [               0-9  A-Za-z       ]                                       ## ranges   NB! excludes i18n addresses
    #d-labels       :=                                         ( <d-label>    .)+
    #d-label        :=                                          [  dl-char ]+                        
    #dl-char        :=                                           -                                  ## literal
    #dl-char        :=                                            0-9A-Za-z                         ## ranges 
    #top-level-d    :=                                                           ([0-9A-Za-z]){2,4} ##          NB! max of 4 is too strict

    # Note that by default, email fields on  clientside forms dont use the above.  Instead they will use the regex provided by AngularJS
    #var EMAIL_REGEXP = /^[a-z0-9!#$%&'*+\/=?^_`{|}~.-]+@[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*$/i;
    #  python str =    r'^[a-z0-9!#$%&\'*+\/=?^_`{|}~.-]+@[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*$'
    # This is broadly similar except for allowing the domain-part to be just a TLD   eg joebloggs@com    
    # it is also lowercase only for use with a case-insensitive search
    #and does not allow domain part to start with '-'
    
    def findNgEMAIL_REGEXP():
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
                    #x = line[-1:]
                    #logging.debug('line end1: %r %d',x, ord(x))
                    # for i in range(4):
                        # x = line[-(i+1):-i]
                        # logging.debug('line end2: %r %d',x, ord(x))
                    found = line
                    break
        if found:
            ngEMAIL_REGEXP = found[len(start):-len(end)]
            logging.debug('regex: %s', ngEMAIL_REGEXP)
            return ngEMAIL_REGEXP
        
        logging.debug('line not found')
        return None
        
    return findNgEMAIL_REGEXP() or EMAIL_REGEX

def uuid():
    """Generates random UUID used as user token for verification, reseting password etc.
    Returns:	string:     32 characters long 
    """
    return uuid4().hex


def create_name_from_email(email):
    """Function tries to recreate real name from email address
    Examples:     >>> create_name_from_email('bobby.tables@email.com')
                  Bobby Tables
                  >>> create_name_from_email('bobby-tables@email.com')
                  Bobby Tables
    Args:		email (string)  : Email address
    Returns:	string          : Hopefully user's real name
    """
    return re.sub(r'_+|-+|\.+|\++', ' ', email.split('@')[0]).title()


def password_hash(password):
    """Hashes given plain text password with sha256 encryption
    Hashing is salted with salt_ configured by admin, stored in >>> model.Config
    Args:		password (string)   : Plain text password
    Returns:	string              : hashed password, 64 characters
    """
    sha = hashlib.sha256()
    sha.update(password.encode('utf-8'))
    sha.update(config.CONFIG_DB.salt_)
    return sha.hexdigest()


def list_to_dict(input_list):
    """Creates dictionary with keys from list values
    This function is primarily useful for converting passed data from Angular checkboxes,
     since angular ng-model can't return list of checked group of checkboxes, instead
     it returns something like {'a': True, 'b': True} for each checkbox
    Example:        >>> list_to_dict(['a', 'b'])
                    {'a': True, 'b': True}
    Args:		input_list (list)   : List of any type
    Returns:	dict                : Dict with 'True' values
    """
    return _.zip_object(input_list, _.map(input_list, _.constant(True)))


def dict_to_list(input_dict):
    """Creates list from dictionary with true booloean values
    This function is primarily useful for converting passed data from Angular checkboxes,
     since angular ng-model can't return list of checked group of checkboxes, instead
     it returns something like {'a': True, 'b': True} for each checkbox
    Example:        >>> dict_to_list({'a': True, 'b': True, 'c': False})
                    ['a', 'b']
    Args:		input_dict (dict): Dict with boolean values
    Returns:	list: list of truthful values
    """
    return _.keys(_.pick(input_dict, _.identity))


def limit_string(string, minlen, maxlen):
    """Validation function constrains minimal and maximal lengths of string.
    Args:		string (string) : String to be checked
                minlen (int)    : Minimal length
                maxlen (int)    : Maximal length
    Returns:	string          : Returns given string
    Raises:	    ValueError      : If string len is out of range
    """
    n = len(string) 
    if n < minlen:
        raise ValueError('Input need to be at least %s characters long' % minlen)
    if maxlen > 0:
        if n > maxlen:
            raise ValueError('Input need to be maximum %s characters long' % maxlen)
    return string


def match_regex(string, regex):
    """Validation function checks validity of string for given regex.
    Args:		string (string) : String to be checked
                regex (string)  : Regular expression
    Returns:	string          : Returns given string
    Raises:		ValueError      : If string doesn't match regex
    """
    h = re.compile(regex, re.IGNORECASE)        # todo store h in app.registry ?
    if not h.match(string):
        raise ValueError('Incorrect regex format')
    return string

def pyProperties(cls):
    '''return a list of names of all the python properties in cls
    NB Normally properties are created with the @property decorator, 
    but they can also be created using property() built-in function, and in other arcane ways. 
    '''
    return [k for k, v in vars(cls).items() if isinstance(v, property)]
    
# coding: utf-8

from __future__ import absolute_import #todo shouldn't we have this on every module or on none?
import logging
from google.appengine.ext import ndb #pylint: disable=import-error
from google.appengine.datastore import datastore_query#.Cursor #pylint: disable=import-error
import re
import util
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

    def init (_s, spec, func):
        def validator (arg1, arg2=None):                   
            #  ndb.property code calls the validator like this :  value = validator (property, value)  
            # but rqParse expects this signature           :      value = validator (value)  
            if arg2 is not None:
                assert isinstance(arg1, ndb.Property) 
                value = arg2 
            else:
                value = arg1  
            
            # if not required and value == '':  #todo delete - We dont need required param do we?
                # return ''
            return func(value, spec)
        
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
email_MinMax  = [3, 254]
uname_MinMax  = [3, 40]
login_MinMax  = [ min( email_MinMax[0]
                     , uname_MinMax[0] )
                , max( email_MinMax[1]
                     , uname_MinMax[1] )
                ]
username_span = lengthVdr(uname_MinMax)
email_span    = lengthVdr(email_MinMax)
loginId_span  = lengthVdr(login_MinMax)
name_span     = lengthVdr([0,100])
password_span = lengthVdr([6, 70])
bio_span      = lengthVdr([0,140])
location_span = lengthVdr([0, 70])
social_span   = lengthVdr([0, 50])
arithExpr_span= lengthVdr([0, 50])

email_rx  = regexVdr(util.getEmailRegex())


######## Custom Validators ##############################################################

def toBool (v):
    if type(v) is bool          : return v
    v = v.lower()
    if v == 'yes'or v == 'true' : return True
    if v == 'no' or v == 'false': return False
    raise ValueError ('Sorry, "%s" is not a valid boolean'% v) 
    

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

def toCursor (cursor):
    """This is a type converter, not merely a validator, it also converts.
    As such should be used with the rqArg "type=" paramenter,  (NOT the "vdr=" parameter)
    
    In this case it converts from a cursor string to a ndb Query Cursor
    and verifies that the given string is valid, returning an instance of ndb Query Cursor.
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

def simpleArithmeticExpr (expr):
    # len(fnStr) <= max
    arithExpr_span.fn (expr)
   
    try: 
        for n in xrange(maxbad):
            eval_expr(expr, {'n': n})
    except ValueError:
        raise
    except:
        ei = sys.exc_info()
    # try:
        # revert_stuff()
    # except:
        # # If this happens, it clobbers exc_info, which is why we had to save it above
        # import traceback
        # print >> sys.stderr, "Error in revert_stuff():"
        # traceback.print_exc()
    raise ei[0], ei[1], ei[2]
    
##################################################
import ast
import operator
import functools


def maxIntermediate (max_=None):
    """ limit magnitude of intermediate results IE at every operation."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*pa, **ka):
            ret = func(*pa, **ka)
            try:
                mag = abs(ret) 
            except TypeError:
                pass    # ret is a branch node, so limit() is not applicable 
            else:       # ret is a leaf node IE a number
                if mag > max_:
                    raise ValueError('overflow: %d'%ret)
            return ret
        return wrapper
    return decorator

def eval_expr (expr, vals):
    """ Examples:
            >>> eval_expr('2^6')
            4
            >>> eval_expr('2**6')
            64
            >>> eval_expr('1 + 2*3**(4^5) / (6 + -7)')
            -5.0
            >>> evil = "__import__('os').remove('important file')"
            >>> eval_expr(evil) #doctest:+IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            ...
            TypeError:
            >>> eval_expr("9**9")
            387420489
            >>> eval_expr("9**9**9**9**9**9**9**9") #doctest:+IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            ...
            ValueError:
    """
    def limited_power(a, b):
        '''to limit input arguments for a**b:'''
        if abs(b) > 20:
            raise ValueError('excessive exponent: %r' %b)
        if abs(a) > 100:
            raise ValueError('excessive mantissa: %r' %a)
        return operator.pow(a, b)

    #def getOp(x):
        # supported operators
    ops = { ast.Add     : operator.add      # +
          , ast.Sub     : operator.sub      # -
          , ast.Mult    : operator.mul      # *
          , ast.Div     : operator.truediv  # /
          , ast.FloorDiv: operator.floordiv # //
          , ast.Pow     : operator.pow      # **    or use limited_power 
          , ast.USub    : operator.neg      # - (unary)
          }
              
    @maxIntermediate(2**32)
    def eval_(x): # x:= node in recursive tree
        if isinstance(x, ast.Num):    
            return x.n                  # actual number  
        if isinstance(x, ast.BinOp):    # <left> <operator> <right>
            return ops[type(x.op)] (eval_(x.left), eval_(x.right))
        if isinstance(x, ast.UnaryOp):  # <op> <operand> EG Node(-1) has {op: ast.USub,  operand:ast.Num(1)}
            return ops[type(x.op)] (eval_(x.operand))
        if hasattr(x,'id'):
            if isinstance(x, ast.Name):
                if x.id in vals:
                    return vals[x.id]
                raise ValueError("Unrecognised name: %s" % x.id) 
            raise ValueError("Unrecognised symbol: %s" % x.id) 
        if isinstance(x, ast.Call):
            raise ValueError("Unrecognised function: %s" % x.func.id) #)
        raise ValueError("Unrecognised node at: %s" % expr[x.col_offset : x.col_offset+4])
        
    return eval_(ast.parse(expr, mode='eval').body)
       
##################################################################################

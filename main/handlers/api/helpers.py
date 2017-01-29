# coding: utf-8
"""
Set of helper function used throughout the REST API
"""
#from google.appengine.datastore.datastore_query import Cursor #pylint: disable=import-error
#from google.appengine.api import urlfetch #pylint: disable=import-error
import logging

import flask_restful as restful
#from werkzeug import exceptions
import flask
#from main import config
#import urllib
#from flask import request
#import json
#import model.user as users
#import validators as vdr
from werkzeug.utils import cached_property

class Api(restful.Api): # pylint: disable=too-few-public-methods
    """By extending restful.Api class we can make custom implementation of some of its methods"""

    def handle_error(self, err):
        """Specifies error handler for REST API which is called when exception is raised during request processing
        Args:    err (Exception): the raised Exception object
        """
        return handle_error(err)


def handle_error(err):
    """This error handler logs exception and provides a response with error message and error code
    Args:   err (Exception): the raised Exception object
    """
    logging.exception(err)
    message = ''
    try:
        if hasattr(err, 'data'):
            message = err.data['message']
        if not message and hasattr(err, 'message'):
            message = err.message
        if not message:
            message = err.description
    except:
        message = 'Unrecognised error format: ' + repr(err)
    try:
        err.code
    except AttributeError:
        err.code = 500
    return flask.jsonify({'message': message}
                        ), err.code


# def make_not_found_exception():
    # """Raises 404 Not Found exception
    # Raises: HTTPException: with 404 code
    # """
    # raise exceptions.NotFound()


# def make_bad_request_exception(message):
    # """Raises 400 Bad request exception
    # Raises:  HTTPException: with 400 code
    # """
    # raise exceptions.BadRequest(message)


def ok():
    """Returns OK response with empty body"""
    return '', 204


def list_response(response_list, cursor=None, more=False, total_count=None):
    """Creates response with list of items and also meta data used for pagination
    Args    : response_list (list)      : list of items to be in response
              cursor (Cursor, optional) : ndb query cursor
              more (bool, optional)     : whether there's more items in terms of pagination
              total_count(int, optional): Total number of items
    Returns : (dict)   : the response to be serialized and sent to client
    """
    return { 'list' : response_list
           , 'meta' : { 'nextCursor': cursor.urlsafe() if cursor else ''
                      , 'more'      : more
                      , 'totalCount': total_count
           }          }

def rqArg(argName, **ka):
    '''syntax sugar to simplify calling RequestParser functions
    EG  rqArg('name', vdr=vdr.specifiedVdr)        ->   ('name', {'vdr' : specifiedVdr.fn})
        rqArg('name', vdr=User.myCustomVdr)        ->   ('name', {'vdr' : myCustomVdr})
    '''
    vdr = None
    if 'vdr' in ka:
        vdr = ka.pop('vdr')
        if not callable(vdr): 
            vdr = vdr.fn
    return argName, vdr, ka
    
def rqParse(*pa):
    '''syntax sugar to simplify calling RequestParser functions    
    Continuing rqArg example ...
    rqParse then further expands these:
                        ->   requestParser.add_argument('name', type=ArgVdr.fn('myVdr'))
                        ->   requestParser.add_argument('name', type=UserVdr.fn('myUserVdr'))
                        ->   requestParser.add_argument('name', type=UserVdr.fn('myUserVdr', required=True))
    '''
    p = restful.reqparse.RequestParser()
    vdrs = {}
    for argName, vdr, ka in pa:
        p.add_argument(argName, **ka) 
        if 'dest' in ka:
            argName = ka['dest']
        vdrs[argName] = vdr
    args = p.parse_args()
    
    assert len(vdrs) == len(args)
    for k,v in vdrs.iteritems():
        if v:
            v(args[k]) #call the validator v with its parsed arg given by args[s]
    return args

#------------------------------------

class Handler (restful.Resource):  #base class for API classes

    @cached_property
    def apiName (_s):
        assert _s.__class__.__name__.endswith('API')
        return _s.__class__.__name__[:-3]

      
    def setLock (_s, lockname, duration):
        def lockOn (kStr, mode, msg): 
            m.Lock.set (kStr, duration, _s.apiName)
            _s.flash ('Too many %s failures: %s for %s.' % ( _s.apiName, msg, u.hoursMins(duration)))
        
        logging.debug('xxxxxxxxxxxxxxxxxxxxxxxxxxx LOCK XXXXXXXXXXXXXXXX')
        if name == 'ipa': # repeated bad attempts with same ipa but diferent ema's
            lockOn (ipa,'Local','you are now locked out')
        elif name == 'ema_ipa':# repeated bad attempts with same ema and ipa
            lockOn (ema,'Local','this account is now locked')
        elif name == 'ema': # repeated bad attempts with same ema but diferent ipa's
            lockOn (ema,'Distributed','this account is now locked')
        
        # todo this password stuff is not generic to other handlers
        pwd = _s.request.get('password')
        logging.warning('%s BruteForceAttack! on %s page: start lock on %s: ema:%s pwd:%s ipa:%s',mode, hlr, name, ema, pwd, ipa)

#------------------------------------

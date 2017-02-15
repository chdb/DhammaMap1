# coding: utf-8
"""
Set of helper function used throughout the REST API
"""
#from google.appengine.datastore.datastore_query import Cursor #pylint: disable=import-error
#from google.appengine.api import urlfetch #pylint: disable=import-error
import logging
#from webapp2 import abort
import json

#import flask_restful as restful
#from werkzeug import exceptions
#import flask
#from main import config
#import urllib
#from flask import request
#import json
#import model.user as users
#import validators as vdr
#from werkzeug.utils import cached_property

# class Api(restful.Api): # pylint: disable=too-few-public-methods
    # """By extending restful.Api class we can make custom implementation of some of its methods"""

    # def handle_error(self, err):
        # """Specifies error handler for REST API which is called when exception is raised during request processing
        # Args:    err (Exception): the raised Exception object
        # """
        # return handle_error(err)

#todo 
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
    return json.dump({'message': message}
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

# def rqArg(argName, **ka):
    '''syntax sugar to simplify calling RequestParser functions
    EG  rqArg('name', vdr=vdr.specifiedVdr)   ->   ('name', {'vdr' : specifiedVdr.fn})
        rqArg('name', vdr=User.myCustomVdr)   ->   ('name', {'vdr' : myCustomVdr    })
    '''
    # vdr = None
    # if 'vdr' in ka:
        # vdr = ka.pop('vdr')
        # if not callable(vdr): 
            # vdr = vdr.fn
    # return argName, vdr, ka
    

# def rqParse(req, *pa):
    '''syntax sugar to simplify calling RequestParser functions    
    Continuing rqArg example ...
    rqParse then further expands these:
        ->   requestParser.add_argument('name', type=ArgVdr .fn('myVdr'))
        ->   requestParser.add_argument('name', type=UserVdr.fn('myUserVdr'))
        ->   requestParser.add_argument('name', type=UserVdr.fn('myUserVdr', required=True))
    '''
    # p = restful.reqparse.RequestParser()
    # vdrs = {}
    # for argName, vdr, ka in pa:
        # p.add_argument(argName, **ka) 
        # if 'dest' in ka:
            # argName = ka['dest']
        # vdrs[argName] = vdr
    # args = p.parse_args(req) # todo pass strict:   parse_args(req, strict=True)
    
    # assert len(vdrs) == len(args)
    # for k,v in vdrs.iteritems():
        # if v:
            # v(args[k]) #call the validator v with its parsed arg given by args[s]
    # return args

#------------------------------------
#------------------------------------

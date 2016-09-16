# coding: utf-8
"""
Set of helper function used throughout the REST API
"""
from google.appengine.datastore.datastore_query import Cursor #pylint: disable=import-error
from google.appengine.api import urlfetch #pylint: disable=import-error
import logging

import flask_restful as restful
from werkzeug import exceptions
import flask
#import model
from main import config
import urllib
from flask import request
import json
import model.user as users
import validators as vdr


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
    return flask.jsonify({'message': message
                        }), err.code


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
    EG  rqArg('name', vdr='myVdr')             ->   ('name', {'type' : ArgVdr.f('myVdr')})
        rqArg('name', vdr='myUserVdr')        ->   ('name', {'type' : UserVdr.fn('myUserVdr')})
        rqArg('name', vdr=('myUserVdr',True)  ->   ('name', {'type' : UserVdr.fn('myUserVdr', required=True)})
    '''
   # def expandArgArgs(vdrName, vdrClass, ka):
            #vdr = getattr(vdrClass,'fn')
            # if isinstance(vdrArg, tuple) and len(vdrArg)==2:      #todo do we need this tuple? -  surely 'required' is redundant on vdr
                # ka['type'] = vdr(vdrArg[0], required=vdrArg[1])
            # else:
                # ka['type'] = vdr(vdrArg) # eg SomeVdr.fn('myVdr')
         
   # expandArgArgs('vdr' , ArgVdr , ka)
   # expandArgArgs('vdr', UserVdr, ka)
    if 'vdr' in ka:
        vdrName = ka.pop('vdr')
        try:
            v = getattr(vdr, vdrName)
        except AttributeError:
            v = getattr(users, vdrName)
        ka['type'] = vdr.fn(v) # eg SomeVdr.fn('myVdr')
    return argName, ka
    
def rqParse(*pa):
    '''syntax sugar to simplify calling RequestParser functions    
    Continuing rqArg example ...
    rqParse then further expands these:
                        ->   requestParser.add_argument('name', type=ArgVdr.fn('myVdr'))
                        ->   requestParser.add_argument('name', type=UserVdr.fn('myUserVdr'))
                        ->   requestParser.add_argument('name', type=UserVdr.fn('myUserVdr', required=True))
    '''
    p = restful.reqparse.RequestParser()
    for a in pa:
        #logging.debug('+++++++++++++++++++++ add arg %r ++++++++',a)
        p.add_argument( a[0], **a[1]) # a is a 2-tuple (argName, kwargs)
        #logging.debug('+++++++++++++++++++++ added arg here ++++++++')
    r = p.parse_args()
    #logging.debug('+++++++++++++++++++++ result %r ++++++++',r)
    return r


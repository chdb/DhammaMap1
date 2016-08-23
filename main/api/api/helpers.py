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
import model
from main import config
import urllib
from flask import request
import json
from model import UserVdr

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


def empty_ok_response():
    """Returns OK response with empty body"""
    return '', 204


def list_response(response_list, cursor=None, more=False, total_count=None):
    """Creates response with list of items and also meta data useful for pagination
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

class Vdr(model.Validator):
    """This validator class contains attributes and methods for validating user's input
   , which is not associated with any particular datastore model, but still needs to be validated
    Attributes: feedback (list): determining min and max lengths of feedback message sent to admin
    """
    feedback = [1, 2000]

    @classmethod
    def captcha(cls, captchaStr):
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


    @classmethod
    def cursor(cls, cursor):
        """Verifies if given string is valid ndb query cursor, if so returns instance of it
        Args    : cursor (string): Url encoded ndb query cursor
        Returns : google.appengine.datastore.datastore_query.Cursor: ndb query cursor
        Raises  : ValueError: If cursor fails
        """
        if not cursor:
            return None
        return Cursor(urlsafe=cursor)


def rqArg(name, **ka):
    '''provides syntax sugar to simplify calling RequestParser functions
    EG  rqArg('name', vdr='myVdr')               ->   ('name', {'type' : Vdr.fn('myVdr')})
        rqArg('name', userVdr='myUserVdr')        ->   ('name', {'type' : UserVdr.fn('myUserVdr')})
        rqArg('name', userVdr=('myUserVdr',True)  ->   ('name', {'type' : UserVdr.fn('myUserVdr', required=True)})
    rqParse then further expands these:
                        ->   requestParser.add_argument('name', type=Vdr.fn('myVdr'))
                        ->   requestParser.add_argument('name', type=UserVdr.fn('myUserVdr'))
                        ->   requestParser.add_argument('name', type=UserVdr.fn('myUserVdr', required=True))
    '''
    def expandArgArgs(argname, vdrClass, ka):
        if argname in ka:
            vargs = ka.pop(argname)
            vdr = getattr(vdrClass,'fn')
            if isinstance(vargs, tuple) and len(vargs)==2:
                ka['type'] = vdr(vargs[0], required=vargs[1])
            else:
                ka['type'] = vdr(vargs)
         
    expandArgArgs('vdr'    , Vdr    , ka)
    expandArgArgs('userVdr', UserVdr, ka)
    return name, ka
    
def rqParse(*pa):
    '''provides syntax sugar to simplify calling RequestParser functions'''
    p = restful.reqparse.RequestParser()
    for a in pa: # a is a 2-tuple
        p.add_argument( a[0], **a[1])
    return p.parse_args()


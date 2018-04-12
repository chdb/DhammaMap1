# coding: utf-8

import logging

logging.debug('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@  main  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')

import handlers
from app import app 

import logging
import os

import json

def handle_error(request, response, exception):
    if(request.path != '/'
    and exception.detail != None):
        #response.headers['Content-Type'] = 'application/json'
        #request.headers['HTTP_ACCEPT'] = 'text/plain' # we want to get a plain response from webob 
                                                # see generate_response() in webob/exc.py lines 310 - 331
                                                # but its not working
        # result = {
            # 'status': 'error',
            # 'status_code': exception.code,
            # 'error_message': exception.explanation,
          # }
        # response.write(json.dumps(result))
        #accept = environ.get('HTTP_ACCEPT', '')
        #a = os.environ.get('HTTP_ACCEPT_LANGUAGE', '')
        # b = os.environ.get('HTTP_ACCEPT', '')
        # logging.debug('xxxxxxxxxxxxxxx exception: %r', exception)
        # logging.debug('xxxxxxxxxxxxxxx exception.detail: %r', exception.detail)
        # logging.debug('xxxxxxxxxxxxxxx HTTP_ACCEPT: %r', b)
        # logging.debug('xxxxxxxxxxxxxxx headers: %r', response.headers)
        # logging.debug('xxxxxxxxxxxxxxx %r', request.headers)
        # logging.debug('xxxxxxxxxxxxxxx %r', accept
        logging.debug('exception = %r',exception)
        logging.debug('exception.detail = %r',exception.detail)
        exception.body = exception.detail
        raise exception
    else:
        response.write(exception)
        response.set_status(exception.code)

# app = webapp2.WSGIApplication()
# app.error_handlers[404] = handle_error
# app.error_handlers[400] = handle_error
# app.error_handlers[401] = handle_error
# app.error_handlers[422] = handle_error

#todo error handling
#currently validation errors call wa2.abort(422)
#but this either generates a html fomatted response(we want plain) from the angular error-interceptor
#or, if we register handle_error for 422, as above,  then the error is not seen by client 
#       unless the exc is re raised
#       ok but still unable to reset the HTTP_ACCEPT header to exclude */* and so make webob to call plain_body() for the plain response

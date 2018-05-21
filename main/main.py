# coding: utf-8

import logging
import util
from app import app
import handlers # pylint: disable=unused-import

logging.debug('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@  main  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')

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

#########################################


class TokenBucket (object):
    '''implement token bucket algorithm without actually using a system timer to insert the token every n milliseconds
    '''
    def __init__(_s):
        _s.tokens = 1                # number of tokens available in the bucket
        _s.lastUpdate = util.msNow() # milliseconds
        #_s.instId = util.randomB64()# this could be moved to be an attribute of app (Note: app is misnamed by GAE: its really an instance.
                                     # The actual app consists of any number of separate concurrent instances. )
        _s.seqNum = 0                # number of tokens dispensed so far

    @staticmethod
    def fromMemCache():
        def modify(dtb):
            b = dtb is None
            if b:
                dtb = DistTokenBucket(TokenBucket())
            return dtb, b

        return util.mcGetSet('tokenBucket', modify)

class DistTokenBucket (object):
    '''Implement the token bucket algorithm to be hosted in MemCache. To cover (most) cases when memcache data
    '''
    def __init__(_s, tb):
        _s.tb = tb
        #_s.instIds = [tb.instId]
        #_s.firstUpdate = None
        #_s.tempToks = 0
        _s.restorePoint = tb.seqNum

    def waitForToken (_s):
        '''return zero: a token is dispensed
           or positive: wait this number of mlliseconds to try again for a token
        '''
        tb = _s.tb
        now = util.msNow()
        ellapsed = now - tb.lastUpdate
        tb.lastUpdate = now
        rate   = app.cfg["TokenBucketRate"]
        bucket = app.cfg["TokenBucketSize"]
        newToks = ellapsed // rate
        tb.tokens = min (tb.tokens + newToks, bucket)
        if tb.tokens <= 0:
            assert rate > ellapsed
            return rate - ellapsed #wait this long (ms) for next token, then try again
        tb.tokens -= 1
        tb.seqNum += 1
        return 0 #caller is hereby given a token

logging.info("88888888888888888")
# init app's copy of TokenBucket
app.tokenBucket = TokenBucket.fromMemCache().tb
logging.info("app = %r", app)
logging.info("app.devt = %r", app.devt)
logging.info("app.tb = %r", app.tokenBucket)
logging.info("app.cfg = %r", app.cfg)

def waitForTokenBucket():
    tb = app.tokenBucket
    def modify(dtb):
        b = dtb is None
        if b:
            dtb = DistTokenBucket(tb)
        elif dtb.restorePoint > tb.seqNum:
            b = True
            dtb.tokens -= dtb.restorePoint - tb.seqNum
        return dtb, b
    dtb = util.mcGetSet('tokenBucket', modify)
    app.tokenBucket = dtb.tb
    return dtb.waitForToken()

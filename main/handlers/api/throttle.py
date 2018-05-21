# coding: utf-8
from functools import wraps
import logging
#import helpers
from google.appengine.api import memcache
#from flask import request, g
from config import cfg_
import util as ut
#from werkzeug import exceptions as exc
#from webapp2 import abort

def credentials(fn):
    @wraps(fn)
    def decorator(handler, *pa, **ka):
        '''parse credentials and pass in as args to handler'''
        args = handler.credentials()
        ka.update(args)
        r = fn(handler, *pa, **ka)
        # if 'user' in r:
            # usr = r['user']
            # if usr is None:
                # handler.abort(401, detail='These credentials are invalid')

            # r['user'] = usr.toDict() #mUser can see her own privates - others cannot
            # if usr.isAdmin_:
                # r['adminCfg'] = CONFIG_DB.toDict()

        return r
    return decorator



def rateLimit(fn): # decorator
    #@cookies
    @wraps(fn)
    def decorator(handler, *pa, **ka):
        #args = getattr(handler, argsFn)()
        logging.debug('££££££££££££ ka %r',ka)
        logging.debug('££££££££££££ pa %r',pa)
        lid = ka.get('loginId')  # if
        c = 'e:' if '@' in lid else 'l:'
        ema = c+lid
        rlt = RateLimiter(ema, handler)
        if not rlt.ready():
            return {'delay':rlt.delay}
        #ka.update(args)
        logging.debug('££££££££££££ ka: %r', ka)

        usr = fn(handler, *pa, **ka) # CALL THE HANDLER

        logging.debug('WWWWWWWWWWWWWWWWW usr %r',usr)
        rlt.tryLock(bool(usr))
        return {'user':usr}
        #todo: instead of auto unlock after n=locktime seconds, after n send user and email with unlock link
    return decorator
#..................................................................
# NB 'bad' in context of the RateLimiter means a request will count towards the lockout count.
# The handler determines which requests are 'bad'.
# Only failed logins are 'bad' requests to rate-limited login handler
#... but all requests to rate-limited forgot handler and signup handler are 'bad'
# because any rapid sequence of requests to those handlers is suspect


LATENCYFACTOR = 50

class RateLimiter(object):

    def __init__(_s, ema, handler):

        def _initDelay(minWait):
            delay = minWait #milliseconds
            for key, cf in _s.monitors.itervalues():
                nBad = _s.mc.get(key)
                if nBad:
                    #logging.debug('extra = %d for %d bad %s logins', cf.delayFn(nBad), nBad, cf.name)
                    delay += cf.delayFn(nBad)
            return delay
            # d = _s.delay*100.0                  # Convert from int-deciseconds to float-milliseconds
            # mcka = cfg_['MemCacheKeepAlive']# Divide d into a series of equal waits so each wait is the max that is less than MemCacheKeepAlive
            # n = -(-d//mcka) # number of waits. NB -(-a//b) rounds up a division and is equivalent to math.ceil(a/b)
            # _s.wait = int(-(-d//n)) # .. round up to int-millisecs

            # logging.debug('delay = %d ms, n = %d, wait = %d ms, total = %d', d, n, _s.wait, _s.wait*n)
            # assert _s.wait <= mcka
            # assert n     * _s.wait >= d
            # assert(n-1) * _s.wait <= d

        def _initMonitors(ema, ipa):

            def _insert(name, keybase):
                assert name in lCfg
                lkey = 'L:'+_s.handler.apiName+':' + keybase
                _s.monitors[name] =(lkey, lCfg[name])

            cfg = cfg_[_s.handler.apiName]
            lCfg = cfg.lockCfg
            _s.monitors = {}
                    # name    ,keybase
            _insert('ema_ipa',_s.ei)
            _insert('ema'    ,ema  )
            _insert('ipa'    ,ipa  )
            return cfg

        _s.handler = handler
        ipa = handler.request.remote_addr
        _s.ei = ema + ipa
        _s.mc = memcache.Client()
        _s.monitors = {}
        cfg = _initMonitors(ema, ipa)
        _s.delay = _initDelay(cfg.minDelay)
   
    def ready(_s):
        '''test if we are ready to call the handler'''
        rtt = 200 # round trip time : todo = const val just for testing
                  # = _s.handler.ssn['rtt']
        now = ut.msNow() # milliseconds
        key = 'W:'+ _s.ei
        expiry = _s.mc.get(key)
        logging.debug('expiry = %r  key = %s',expiry, key)
        if expiry:
            if expiry <= now:
                _s.mc.delete(key)
                return True #handler state 'good':-> | 'bad' | 'locked'
        else: # key not found
            exp = _s.delay +(rtt * LATENCYFACTOR) # exp = relative expiry = delay+maxLatency. For maxLatency, rtt * LatencyFactor gives a v rough upper limit
            _s.mc.set(key, now+_s.delay, exp)
        return False

    def tryLock(_s, ok):
        '''having called the handler, with result of 'ok', decide whether to wipe the slate, increment the bad count, or set a lock out'''
        def update(lockname):
            key, cfg = _s.monitors[lockname]
            nBad = _s.mc.get(key) # number of previous consecutive bad attempts
            if nBad:
                if ok:
                    if cfg.bGoodReset:
                        _s.mc.delete(key)
                else:
                    if nBad < cfg.maxbad:
                        _s.mc.incr(key)
                    else:
                        _s.mc.delete(key)
                        _s.handler.setLock(lockname, cfg.lockTime)
                return True
            if not ok:
                exp = ut.sNow() + cfg.period #need use absolute time to keep same exp time when calling mc.set
                _s.mc.set(key, 1, exp)
            return False

        if not update('ema_ipa'):
            update('ema')
            update('ipa')
        return not ok

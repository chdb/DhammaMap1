# coding: utf-8
import logging
import helpers
from google.appengine.api import memcache
from flask import request, g
from config import cfg_
import util as ut
from werkzeug import exceptions as exc

        
def rateLimit (fn):
    #@cookies 
    def _rateLimit (handler, *pa, **ka):        # handler is for handler
        ipa = request.remote_addr
        ema = g.args.loginId 
        rlt = RateLimiter (ema, ipa, handler)
        if not rlt.ready ():
            return {'delay': rlt.delay}
        resp = fn (handler, *pa, **ka) # CALL THE HANDLER
        if rlt.tryLock (resp): 
            raise exc.Unauthorized('These credentials are invalid')
        return resp
        #todo: instead of auto unlock after n=locktime seconds, after n send user and email with unlock link 

    return _rateLimit
#..................................................................
# NB 'bad' in context of the RateLimiter means a request will count towards the lockout count.
# The handler determines which requests are 'bad'. 
# Only failed logins are 'bad' requests to rate-limited login handler 
#... but all requests to rate-limited forgot handler and signup handler are 'bad' 
# because any rapid sequence of requests to those handlers is suspect

class RateLimiter (object):
    
    def __init__(_s, ema, ipa, handler):
        
        def _initDelay (minWait):
            _s.delay = minWait #milliseconds
            for key, cf in _s.monitors.itervalues():
                nBad = _s.mc.get (key)
                if nBad:
                    #logging.debug('extra = %d for %d bad %s logins', cf.delayFn(nBad), nBad, cf.name)
                    _s.delay += cf.delayFn(nBad)
            # d = _s.delay*100.0                  # Convert from int-deciseconds to float-milliseconds 
            # mcka = cfg_['MemCacheKeepAlive']# Divide d into a series of equal waits so each wait is the max that is less than MemCacheKeepAlive
            # n = -(-d//mcka) # number of waits. NB -(-a//b) rounds up a division and is equivalent to math.ceil (a/b)
            # _s.wait = int(-(-d//n)) # .. round up to int-millisecs
            
            # logging.debug('delay = %d ms, n = %d, wait = %d ms, total = %d', d, n, _s.wait, _s.wait*n)
            # assert _s.wait <= mcka
            # assert n     * _s.wait >= d
            # assert (n-1) * _s.wait <= d
        
        def _initMonitors (ema, ipa):
        
            def _insert (name, keybase):
                assert name in lCfg
                _s.monitors[name] = ('L:'+_s.handler.apiName+':'+keybase, lCfg[name])

            cfg = cfg_[_s.handler.apiName]
            lCfg = cfg.lockCfg
            _s.monitors = {}
                    # name    ,keybase  
            _insert ('ema_ipa',_s.ei)
            _insert ('ema'    ,ema  )
            _insert ('ipa'    ,ipa  )       
            return cfg
        
        _s.handler = handler
        _s.ei = ema + ipa
        _s.mc = memcache.Client()        
        cfg = _initMonitors (ema, ipa)
        _initDelay (cfg.minDelay)       

             
    def ready (_s):
        rtt = 200 # todo = const val just for testing   
                  # = _s.handler.ssn['rtt']
        now = ut.msNow() # milliseconds
        key = 'W:'+ _s.ei
        expiry = _s.mc.get (key)
        logging.debug('expiry = %r  key = %s',expiry, key)
        if expiry:
            if expiry <= now:
                _s.mc.delete (key)
                return True #handler state 'good':-> | 'bad' | 'locked'
        else: # key not found 
            LatencyFactor = 50
            exp = _s.delay + (rtt * LatencyFactor) # exp = relative expiry = delay+maxLatency. For maxLatency, rtt * LatencyFactor gives a v rough upper limit 
            _s.mc.set (key, now+_s.delay, exp)  
        return False                                   

        
    def tryLock (_s, ok):
        ''''''
        def update (lockname):
            key, cfg = _s.monitors[lockname]
            nBad = _s.mc.get (key)
            if nBad: 
                if ok:
                    if cfg.bGoodReset:
                        _s.mc.delete (key)
                else:    
                    if nBad < cfg.maxbad:
                        _s.mc.incr (key)
                    else: 
                        _s.mc.delete (key)
                        _s.handler.setLock(lockname, cfg.lockTime)
                return True
            if not ok: 
                exp = ut.sNow() + cfg.period #need use absolute time to keep same exp time when calling mc.set
                _s.mc.set (key, 1, exp)
            return False
        
        if not update('ema_ipa'):
            update('ema')
            update('ipa')
        return not ok

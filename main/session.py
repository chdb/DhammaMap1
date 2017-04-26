#!/usr/bin/python
# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import logging
import kryptoken
import util as u
#import debug as d
from model.user import User
import webapp2
# # # # # # # # # # # # # # # # # # # # 

class CookieNameError(ValueError):
    pass

class Cookie (object):
    def __init__(_s, cookieName, path='/', domain=None, secure=None, httponly=True):
        if secure is None:
            secure = not webapp2.get_app().debug
        _s.cfg = { 'key'     : cookieName
                 , 'path'    : path
                 , 'domain'  : domain
                 , 'secure'  : secure #not handler.app.debug
                 , 'httponly': httponly
                 }
  
    def set       (_s, handler, val): _s._set(handler, val, checkExists=True , resetting=False) # exception if already exists
    def reset     (_s, handler, val): _s._set(handler, val, checkExists=True , resetting=True ) # exception if doesnt exist
    def setOrReset(_s, handler, val): _s._set(handler, val, checkExists=False) # force a cookie to set or reset - you dont care which
    
    def _set (_s, handler, val, checkExists, resetting=False):
        # NB webOb treats cookie-name as a unique key called 'key' and uses a dict for a key-value map. 
        # This is similar to other frameworks but it hides a peculiarity of cookies. 
        # There can be multiple cookies with same name in the request's cookie header, because for the client, Cookie-name is not the full key;    
        # The client identifies cookies by (name, path, domain) IE a different path or domain identifies a different cookie. 
        # This is why we need path and domain from our cfg for delete() and reset() to work properly. 
        # For each request (for a given url - ie domain + path) the client will send all cookies matching a given name and url.
        # However webOb, like most server frameworks, will only read first one from the cookie header. 
        # The cookie which had longest url, ie most specific, *should* be the first one but might not be.
        # MORAL -- if, in same domain, you are using various cookies for different paths or sub-domains, be sure to use different cookie names for each.
        exists = bool(_s.get(handler))
        if checkExists:
            if resetting:
                if not exists:
                    raise CookieNameError('This cookie name is not in use.')
            else:
                if exists:
                    raise CookieNameError('This cookie name is already in use.')
        
        n = len(val)
        if n > 4093: #some browsers will accept more but this is about the lowest browser limit
            raise ValueError('Cookie size is %d bytes and exceeds max: 4093', n)
        #todo:what to do? too big for cookie!!!
        #logging.debug ('setting cookieMgr = %r', val)
                
        handler.response.set_cookie (value=val, **_s.cfg)
        
    def get (_s, handler):
        val = handler.request.cookies.get (_s.cfg['key'])
        if val:
            val = val.encode('utf-8') #from unicode to bytes
        #logging.debug ('cookieMgr data = %r', val)
        return val
        
    def delete (_s, handler):
        # As close as possible to a delete of browser cookie. (Browsers provide no deleteCookie method - you must overwrite setting expiry to zero or negative lifespan) 
        # When client gets the response, only the cookie value is immediately deleted IE overwritten with empty string.
        # The expiry is set to zero and the name will usually remain visible intil cookie itself is deleted when the browser window closes. 
        cfg = {k:_s.cfg[k] for k in ('key','path','domain')}
        # logging.debug('cfg = %r', cfg)
        handler.response.delete_cookie (**cfg)
                  
# # # # # # # # # # # # # # # # # #

class _UpdateDictMixin (object):
    """A dict which calls `_s.on_update` on all modifying function calls."""
    on_update = None

    def calls_update (name):
        def oncall (_s, *args, **kw):
            rv = getattr (super (_UpdateDictMixin, _s), name)(*args, **kw)
            if _s.on_update is not None:
                _s.on_update()
            return rv
        oncall.__name__ = str(name)
        return oncall

    __setitem__= calls_update('__setitem__')
    __delitem__= calls_update('__delitem__')
    clear      = calls_update('clear'      )
    pop        = calls_update('pop'        )
    popitem    = calls_update('popitem'    )
    setdefault = calls_update('setdefault' )
    update     = calls_update('update'     )
    del calls_update

##todo  separate Session (ie dict etc) from SessionVw
##          make session a namedtuple (_created gets overwiteen in Kryptoken.encode)
##      separate Flashes 
##          make it a member class

class SessionVw (_UpdateDictMixin, dict):
    """ SessionVw looks like a session but its really just a view- a snapshot of a session. It has same 
    data but lasts only for a request lifetime, retrieving the session data from the session cookieMgr.
    """
    __slots__ = ('modified') # 'container', 'new', is not used
    #_userKey = '_u'

    def __init__ (_s, handler):  # container, , new=False
        logging.debug('#################### SessionVw __init__ called')  
        _s.modified = False
        _s.handler = handler
        _s.cookie = Cookie('dm_session')
        cookieVal = _s.cookie.get(handler)
#        token = handler.request.headers.get('authentication')
       # data = kryptoken.decodeToken (token, 'session') if token else {}
        if cookieVal:
            # n = len(_s.cookieVal)
            # if n < cryptoken.MinTokenLen:
                # if n != _s.nonceLen:
                    # logging.warning('cookieMgr has unexpected length: %d', n)
                # data = _s.midStore.get(_s.cookieVal)
                # #todo get expired from data
            # else:
            data = kryptoken.decodeToken (cookieVal, 'session')
            if data:
                assert type(data) is dict
            if not '_created' in data:
                data['_created'] = u.sNow()          
            dict.update (_s, data)

    def expired (_s): 
        if _s.isLoggedIn(): 
            return u.expired (_s['_logInTS'], 'auth') 
        return False # ANON sessions do not expire

    def save (_s):
        if _s.modified:
            val = kryptoken.encodeSessionToken (_s) #, user
            #_s.handler.response.headers['authentication'] = val
            logging.debug('saving session                                        £££££££££££££££££')
            _s.cookie.setOrReset(_s.handler, val)
            
    def on_update (_s):
        _s.modified = True
        
    # def pop (_s, key, *args):
        # if key in _s:
            # return super(SessionVw, _s).pop (key, *args)# Only pop if key exists
        # if args:
            # return args[0] # no key so return the default val specified at args[0]
        # raise KeyError (key)

    # 2 funcs to maintain a list of msg items at key='_flash'
    # Each msg item is a duple (msg, level)
    def getFlashes (_s): #, key='_flash'
        """NB The list of Flash messages is deleted when read. """
        return _s.pop ('_flash', [])             # returns a list of duples: [(msg, level), ...]

    def addFlash (_s, msg, level=None): #, key='_flash'
        '''add a (msg, level) to the list
        NB. Caller of this func must ensure the msg content is safe from injection attack. 
        Especially if it contains results from a form input. Form input should be validated server-side
        (also on client-side if possible). Any text fields that are not entirely alphanumeric are suspect.
        The msg either must be TRUSTED content (ie without any non-alphanumeric user input) 
        or else it must be html ESCAPED content, before passing to flash()
        because this msg will inserted in the template html body WITH AUTOESCAPE OFF
        '''
        _s.setdefault ('_flash', []).append((msg, level))  # append to duple list:  [(msg, level), ...]

    def logIn (_s, user, ipa, remember ):
        logging.debug('user = %r', user)
        _s['_userID' ]= user.id()
        _s['_logInTS']= u.sNow()
        _s['_sessIP' ]= ipa
        
       # _s['_sessID'] = sid = utils.newSessionToken()
       # user.token = sid
       # user.modified = True
        logging.debug('just logged in ssn = %r',_s)
        logging.debug('just logged in ssn id = %r',id(_s))
        
    def logOut (_s):
        # if user:
            # user.token = ''
            # user.modified = True
        # _s.pop('_userID' , None) # default arg (None) to avoid KeyError
        # _s.pop('_logInTS', None)
        # _s.pop('_sessIP' , None) 
      #  d.logStackTrace(3)
        # logging.debug('about to logout ssn = %r',_s)
        # logging.debug('about to logout  ssn id = %r',id(_s))
        _s.cookie.delete(_s.handler)
        uid = _s.pop('_userID', None)# default arg (None) to avoid KeyError
        # logging.debug('2 uid was = %r', uid)
        if uid is not None:
            del _s['_logInTS']
            del _s['_sessIP' ]            
            return True
        return False

    def isLoggedIn (_s):  
        return ('_logInTS'in _s   # \   # and '_sessID' in _s \
        and     '_sessIP' in _s 
        and     '_userID' in _s)
         
        #    if user:
              #  if user.sameToken(_s['_sessID']):
         #return False

    def hasLoggedInRecently (_s, maxAge):
        timeStamp = _s['_logInTS']
        return u.validTimeStamp (timeStamp, maxAge)
     
    
    #   3) encode(new) to save IP address when new==True to memcache and 
    #   4) decode(new) to compare IP when new==False and if different decode() fails unless memcache fails
    #   
#from google.appengine.api import memcache
    
# def get (handler):
    # ssn = _get (handler.request)
    # logging.info('get ssn items:||||||||||||||||||')
    # for k, v in s.iteritems():
        # logging.info('         %s : %s', k, v)
    # logging.info('|||||||||||||||||||||||||||||||||||||')

 # if not ssn:
    # ssn['lang'] = 'en'
    # _save (handler, ssn)
    # handler.redirect_to('nocookie', abort=True)
    
    
   # cookieWasSet = memcache.get(ssn['_userID'] + 'x') 
#        if cookieWasSet:
 #           ssn.addFlash('There seems to be a problem reading the browser cookieMgr. Please ensure cookies are not disabled.')
    # return ssn
    
# import traceback as tb


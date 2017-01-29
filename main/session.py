#!/usr/bin/python
# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

import logging
import kryptoken
import utils as u
import debug as d
from models import User

from flask import request
# from midstore import MidStore

def loadConfig(app):

    default_config ={ 'maxIdleAnon' : None
                    , 'maxIdleAuth' : 60 * 60 # 1 hour
                    , 'cookieName'  : 'dm_session'
                                     # for effect of cookieArgs see defn of Response.set_cookie() at ...\google_appengine\lib\webob-1.2.3\webob\response.py line 690
                    , 'cookieArgs'  : { 'max_age' : None  # for persistent cookies - but use expires instead for IE 8
                                      , 'domain'  : None
                                      , 'path'    : '/'
                                      , 'secure'  : not app.debug
                                      , 'httponly': True
                                      }
                    } 
    #default_config.update(app.config)
    #app.config = default_config
    app.config.load_config ( key=__name__
                           , default_values=default_config
                           #, user_values 
                           #, required_keys =('secret_key',)
                           )

# def cfg(handler):
    # return handler.app.config [__name__]
    
# # # # # # # # # # # # # # # # # # # # 

class CookieMgr (object):
    def __init__(_s, handler):
        _s.handler = handler
        _s.cfg = u.config(__name__)
        _s.name = _s.cfg['cookieName']    

    def set (_s, val):
        args = _s.cfg['cookieArgs']
        _s.handler.response.set_cookie (_s.name, val, **args)
        
    def get (_s):
        val = _s.handler.request.cookies.get (_s.name)
        if val:
            val = val.encode('utf-8') #from unicode to bytes
        #logging.debug ('cookieMgr data = %r', val)
        return val
        
    def delete (_s):
        args= _s.cfg['cookieArgs']
        path  = args.get('path')
        domain= args.get('domain')
        _s.handler.response.delete_cookie (_s.name, path, domain)
                  
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
        token = handler.request.headers.get('authentication')
        data = kryptoken.decodeToken (token, 'session') if token else {}
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
        ssn = _s.handler.ssn
        if ssn and ssn.modified:
            val = kryptoken.encodeSessionToken (ssn) #, user
            _s.handler.response.headers['authentication'] = val
        
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

    def logIn (_s, user, ip):
        logging.debug('1 uid = %r', user.id())
        _s['_userID' ]= user.id()
        _s['_logInTS']= u.sNow()
        _s['_sessIP' ]= ip
        
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
        d.logStackTrace(3)
        logging.debug('about to logout ssn = %r',_s)
        logging.debug('about to logout  ssn id = %r',id(_s))
        uid = _s.pop('_userID', None)# default arg (None) to avoid KeyError
        logging.debug('2 uid was = %r', uid)
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


 # coding: utf-8
"""
Initializes flask server and assigns all routes by importing modules

TODO A) replace flask with webapp2
        1)  routes - replace flask and flask_restfiul with wa2 route map - implement and test one by one
            session - replace flask session and flask-login with custom
        2)  config - finish new config design with secret.py etc
            and jinja config
     B) API(both client and server) - use base64(int ndb.entity.id()) instead of ndb.key.urlsafe() for user id etc  
"""
# import flask
#import util
import config
import logging

logging.debug('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@  main  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')

from functools import wraps 
# Third party libraries path must be findable before importing webapp2
#sys.path.insert(0, os.path.join (os.path.dirname(__file__), 'Libs'))
import webapp2
import re

# first_cap_re = re.compile('(.)([A-Z][a-z]+)')
# all_cap_re = re.compile('([a-z0-9])([A-Z])')
# def convert(name):
    # s1 = first_cap_re.sub(r'\1_\2', name)
    # return all_cap_re.sub(r'\1_\2', s1).lower()
    
camel = re.compile('((?<=[a-z0-9])[A-Z]|(?<=[A-Z])[A-Z](?=[a-z]))')
def camel2spine (s):
    return camel.sub(r'-\1', s).lower()

# def _route (s, urlPrefix, hlrPrefix, *pa, **ka): 
    # Get the uriTemplate 'u' from the 's' parameter
    #       EG route('aB-c/EFg/<pqr>/<xyz>')
    #          u == '/ab-c/efg/<pqr>/<xyz>'   
    # Get the 'name' from the 's' parameter
    #       EG route('aB-c/EFg/<pqr>/<xyz>')
    #       name ==  'aBcEFg_pqr'   
    # assert not s.startswith('/') 
    # assert not s.endswith('/') 
     
    # u = urlPrefix + camel2spine(s) # u := uri OR uri template

    # if len(pa) <= 1 and 'name' not in ka: # 1: 'name' would be pa[1]
        # name = s
        # m = re.search( r'([^/]+)(/<(.+):?.*>)?$', s) # find groups parenthized by < : >
        # if m:
            # name = m.group(1)
            # p = m.group(3)
            # if p:
                # name += '_' + p # append the first find 
        # ka['name'] = name
        
    # if len(pa) <= 0 and 'handler' not in ka: # 0: 'handler' would be pa[0]
        # ka['handler'] = eval (hlrPrefix + name)
 
    # assert len(u) < 40      # ok - an abritrary max url len, but hey, its just for formatting the log
    # tab = ' '*(40-len(u))   # ok anyway, because for n < 0,  'x'*n   is  ''
    # logging.info('route pa = %r%s%r %r', u, tab, pa, ka)
    
    # return webapp2.Route (u, *pa, **ka)#, handler_method=hm, methods=ms, **ka)

# def apiRoute (s, *pa, **ka): return _route(s, '/api/v1/', 'handlers.api.v1.H', *pa, **ka)
# def route_   (s, *pa, **ka): return _route(s, '/'       , 'handlers.H'       , *pa, **ka)
    
# rts=[ route('_ah/Warmup' )
    # , route('', handlers.HHome, 'Home') # positional pa follow order for webapp2.Route( template, handler name, ... )
    # , apiRoute('auth/SignUp'  )
    # , apiRoute('auth/LogIn'   )
    # , apiRoute('auth/LogOut'  )
    # , apiRoute('auth/ResendSignUp')
    # , apiRoute('auth/ForgotPassword')
    # , apiRoute('auth/ResetPassword' )
    # , apiRoute('Config' )
    # , apiRoute('Users' )
    # , apiRoute('NumUsers' )
    # ]

    # , webapp2.Route('/api/v1/auth/Signin' , handler=h.api.v1.HSignin, name='SigninAPI')
   # , route ('NoCookie'                )
    # , route ('NoCookie'                )
    # , route ('Signup'                  )
    # , route ('Signup/msg'              , handler_method='get2' , methods=['GET' ])
    # , route ('Signup/<token>'          )
    # , route ('Forgot'                  )
    # , route ('Forgot/a'                , handler_method='post2', methods=['POST'])
    # , route ('Login'                   )
    # , route ('Logout'                  )
    # , route ('Secure'                  )
    # , route ('NewPassword/<token>'     )
    # , route ('TQSendEmail'             )                           
    # , route ('TQVerify'                )
    # , route ('Admin/'                  ) 
    # , route ('Admin/NewKeys'           ) 
    # , route ('Admin/Users/'            )
    # , route ('Admin/Users/<uid>/'      , handler_method='edit')
    # , route ('Admin/Logout/'           )
    # , route ('Admin/Logs/Emails/'      )
    # , route ('Admin/Logs/Emails/<eid>/')
    # , route ('Admin/Logs/Visits/'      )
    # , wa2.Route ('/crontasks/purgeAuthKeys/'     , h.H_PurgeAuthKeys    , 'Crontasks-purgeAuthKeys'     )
     
#    myConfig.cfg['Env'] = 'Dev' if os.environ['SERVER_SOFTWARE'].startswith('Dev') else 'Prod'
#cfg = config.init()

# logging.debug('rts : %r',rts)
# for r in rts:
    # logging.debug('         r : %r',r)
# for k,v in config.appCfg.__dict__.iteritems():
    # logging.debug('appCfg : %r\t%r',k,v)
    
class WSGIApp (webapp2.WSGIApplication):
    # def __init__(_s, *pa, **ka):
        # super(WSGIApplication, _s).__init__(*pa, **ka)
        # _s.router.set_dispatcher(_s.__class__.custom_dispatcher)

    # @staticmethod
    # def custom_dispatcher(router, request, response):
        # rv = router.default_dispatcher(request, response)
        # if isinstance(rv, basestring):
            # rv = webapp2.Response(rv)
        # elif isinstance(rv, tuple):
            # rv = webapp2.Response(*rv)

        # return rv
    
    @staticmethod
    def _route (urlPrefix, name_, cls, *pa, **ka): 
        # Get the uriTemplate 'u' from the 'name_' parameter
        #       EG route('aB-c/EFg/<pqr>/<xyz>')
        #          u == '/ab-c/efg/<pqr>/<xyz>'   
        # Get the 'name_' from the 'name_' parameter
        #       EG route('aB-c/EFg/<pqr>/<xyz>')
        #       name_ ==  'aBcEFg_pqr'   
        assert not name_.startswith('/'), '%s' % name_ 
        assert not name_.endswith  ('/'), '%s' % name_ 
         
        u = urlPrefix + camel2spine(name_) # u := uri OR uri template

        if len(pa) <= 1 and 'name' not in ka: # 1: 'name' would be pa[1]
            m = re.search( r'([^/]+?)(/<[^:>]*:?([^>]*)>?(/([^/]*))?)?$', name_) # find groups parenthized by < : >
            if m:
                name_ = m.group(1)
                p = m.group(3)
                if p:
                    name_ += '_' + p # append the first find 
                p = m.group(5)
                if p:
                    name_ += '_' + p # append the first find 
            ka['name'] = name_
           
        if len(pa) <= 0 and 'handler' not in ka: # 0: 'handler' would be pa[0]
            ka['handler'] = cls
     
        assert len(u) < 40      # ok - an abritrary max url len, but hey, its just for formatting the log
        tab = ' '*(40-len(u))   # ok anyway, because for n < 0,  'x'*n   is  ''
        ka2 = dict(ka)
        hndlr = ka2.pop('handler',None)
        name2 = ka2.pop('name',None)
        logging.info('route pa = %r%s%r\t\t%r\t\t%r %r', u, tab, name2, hndlr, pa, ka2)
        
        return webapp2.Route (u, *pa, **ka)#, handler_method=hm, methods=ms, **ka)
        
       
       
    def route_(_s, urlPrefix, name_, *pa, **ka):
        def wrapper(cls):
            
            r = WSGIApp._route(urlPrefix, name_, cls, *pa, **ka)
            #logging.debug('route = %r',r)
            _s.router.add(r)
            return cls
        return wrapper

    def api1Route (_s, name_, *pa, **ka): return _s.route_('/api/v1/', name_, *pa, **ka)
    def route     (_s, name_, *pa, **ka): return _s.route_('/'       , name_, *pa, **ka)
  
   
app = WSGIApp( debug = config.appCfg.development
           # , rts
           # , config=cfg
             )

#    session.loadConfig(wa)   # override/add-to  session config defaults with myConfig               
#    logging.debug('config = %r', a.config)

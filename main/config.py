# coding: utf-8
"""
Global config variables. Config variables stored in DB are loaded into CONFIG_DB variable
"""
#pylint: disable=import-error
import util
from env import ENV
#from jinja_boot import set_autoescape
from collections import namedtuple

# DelayCfg = namedtuple('DelayCfg', ['delay'     # 
                                  # ,'latency'   # milliseconds - maximum time for network plus browser response
                                  # ])           # ... after this it will try again. Too small will prevent page access for slow systems. Too big will cause 
                                                #Todo: set latency value at runtime from multiple of eg a redirect
RateLimitCfg= namedtuple('RateLimitCfg', [ 'minDelay'      #
                                         , 'lockCfg'    # 
                                         ] )
LockCfg     = namedtuple('LockCfg'     , [ 'delayFn'   # lambda(n) - minimum time between requests in milliseconds as function of the retry number.
                                         , 'maxbad'    # number consecutive 'bad' requests in 'period' to trigger lockout
                                         , 'period'    # seconds - time permitted for < maxbad consecutive 'bad' requests
                                         , 'lockTime'  # seconds - duration of lockout
                                         , 'bGoodReset'# boolean - whether reset occurs for good login
                                         ] )                                     
                                        
cfg_={'DebugMode'         : True    #if True, uncaught exceptions are raised instead of using HTTPInternalServerError.
                                   # so that you get a stack trace in the log
                                   #otherwise its just a '500 Internal Server Error' 
    ,'locales'           : []
                         # seconds- 0 means never expire
   #  'maxAgeRecentLogin' : 60*10  
    ,'maxAgeSignUpTok'   : 60*60*24
    ,'maxAgePasswordTok' : 60*60  
    ,'maxAgePassword2Tok': 60*60  
    #,'maxIdleAnon'       : 0 #60*60  
    ,'maxIdleAuth'       : 15 #60*60  
    
    ,'MemCacheKeepAlive' : 500 # milliseconds - to refresh MemCache item, so (probably) not be flushed    

    ,'Signin'   :   RateLimitCfg ( 700
               # milliseconds - minimum time between requests.
            # delay or lock on repeated requests from the same ipa and the same ema
          , {'ema_ipa':LockCfg( lambda n: (n**2)*100 # *10 # 100 200 400 800 1600...
                              , 3      #maxbad
                              , 60*1   #period
                              , 60*3   #lockTime
                              , True   #bGoodReset
                              ) 
            # delay orlock onrepeated requests from the same ema but different ipa's
            ,'ema'    :LockCfg( lambda n: (n-1)*300 # 0 300 600 900 1200...
                              , 3      #maxbad
                              , 60*1   #period
                              , 60*3   #lockTime
                              , True   #bGoodReset
                              )
            # delay orlock onrepeated requests from the same ipa but different ema's
            ,'ipa'    :LockCfg( lambda n: (n-1)*500 # 0 500 1000 1500 2000 ...
                              , 3      #maxbad
                              , 60*1   #period 
                              , 60*3   #lockTime
                              , True   #bGoodReset
          ) }                 )              
    ,'Forgot':RateLimitCfg( 500    # milliseconds- minimum time between requests.
          , {'ema_ipa':LockCfg( lambda n: (n**2)*100 # 100 200 400 800 1600...
                              , 3      #maxbad
                              , 60*1   #period
                              , 60*3   #lockTime
                              , True   #bGoodReset
                              ) 
            ,'ema'    :LockCfg( lambda n: (n-1)*300 # 0 300 600 900 1200...
                              , 3      #maxbad
                              , 60*1   #period
                              , 60*3   #lockTime
                              , True   #bGoodReset
                              )
            ,'ipa'    :LockCfg( lambda n: (n-1)*500 # 0 500 1000 1500 2000 ...
                              , 3      #maxbad
                              , 60*1   #period 
                              , 60*3   #lockTime
                              , True   #bGoodReset
          ) }                 )              
    # ,'pepper'             : None          
    # ,'recordEmails'       : True
    # ,'email_developers'   : True
    # ,'developers'         : (('Santa Klauss', 'snowypal@northpole.com'))
    
    #add-to/update the default_config at  \webapp2_extras\jinja2.py
    # ,'webapp2_extras.jinja2':  { 'template_path'   : [ 'template' ]
                               # , 'environment_args': { 'extensions': ['jinja2.ext.i18n'
                                                                     # ,'jinja2.ext.autoescape'
                                                                     # ,'jinja2.ext.with_'
                                                                     # ]
                                                    # , 'autoescape': set_autoescape
                                                     # }
                               # }
    }
cfg_['Signup'] = cfg_['Forgot']
        

def init():
    util.debugDict(ENV)
    util.debugDict(cfg_)
    
    assert util.disjointDictKeys(ENV, cfg_), '1) No key should be in both dicts.'
 
 #   cfg.update(cfg_)   # todo remove or stringify functions etc  - not jsonisable
                        # also, for security, throttle settings are admin only
                        
    from model.config import CONFIG_DB # NB The model module needs to be imported *after* setting CURRENT_VERSION_TIMESTAMP,
            # since model.ndbModelBase uses it as default value for version_r property

    cfg = CONFIG_DB.toDict()
    assert util.disjointDictKeys(cfg, ENV), '2) No key should be in both dicts.'
    cfg.update(ENV)

    return cfg
    
 
class TwoWayDict(dict):
    def __setitem__(_s, key1, key2):
        # Remove any previous connections with these keys
        if not key1.endswith(':'):
            raise ValueError('key1 is invalid')
        if key1 in _s:
            raise ValueError('key1 not unique')
        if key2 in _s:
            raise ValueError('key2 not unique')
        dict.__setitem__(_s, key1, key2)
        dict.__setitem__(_s, key2, key1)


authNames = TwoWayDict()
# follow the convention: all short names end in ':' (and long names dont)
# follow the convention: all builtin names start with '_' (both short and long names)
authNames ['_e:'] = '_email'
authNames ['_u:'] = '_userName'
authNames ['tt:'] = 'twitter'       # OAuth 1.0a
authNames ['fb:'] = 'facebook'      # OAuth 2.0
authNames ['gg:'] = 'google'        # OAuth 2.0
authNames ['gh:'] = 'github'        # OAuth 2.0
authNames ['li:'] = 'linkedin'      # OAuth 2.0
authNames ['ig:'] = 'instagram'     # OAuth 2.0 but not yet impl in authomatic

# authNames ['bb:'] = 'bitbucket'   # OAuth 1.0a
# authNames ['fk:'] = 'flickr'      # OAuth 1.0a
# authNames ['pk:'] = 'plurk'       # OAuth 1.0a
# authNames ['tb:'] = 'tumblr'      # OAuth 1.0a
# authNames ['ub:'] = 'ubuntuone'   # OAuth 1.0a but UbuntuOne service is no longer available
# authNames ['vm:'] = 'vimeo'       # OAuth 1.0a
# authNames ['xr:'] = 'xero'        # OAuth 1.0a
# authNames ['xg:'] = 'xing'        # OAuth 1.0a
# authNames ['yh:'] = 'yahoo'       # OAuth 1.0a
# authNames ['am:'] = 'amazon'      # OAuth 2.0
# authNames ['be:'] =  'behance'    # OAuth 2.0 but doesn't support third party authorization anymore.
# authNames ['bl:'] = 'bitly'       # OAuth 2.0
# authNames ['dv:'] = 'deviantart'  # OAuth 2.0
# authNames ['fs:'] = 'foursquare'  # OAuth 2.0
# authNames ['pp:'] = 'paypal'      # OAuth 2.0
# authNames ['rd:'] = 'reddit'      # OAuth 2.0
# authNames ['vk:'] = 'vk'          # OAuth 2.0
# authNames ['wl:'] = 'windowslive' # OAuth 2.0
# authNames ['ym:'] = 'yammer'      # OAuth 2.0
# authNames ['yd:'] = 'yandex'      # OAuth 2.0
# authNames ['ol:'] = 'openid_livejournal'   # OpenID
# authNames ['ov:'] = 'openid_verisignlabs'  # OpenID
# authNames ['ow:'] = 'openid_wordpress'     # OpenID
# authNames ['oy:'] = 'openid_yahoo'         # OpenID



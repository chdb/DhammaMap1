# coding: utf-8
"""
Global config variables. Config variables stored in DB are loaded into CONFIG_DB variable
"""
import os
from datetime import datetime
from google.appengine.api import app_identity #pylint: disable=import-error
import util
import logging 


# It is simple and convenient to create some configuration data here in the config file 
# but other config data is stored in ndb DataStore because
# 1) Source Code is not a secure location for cryptographic keys and other secrets because our code base is open-source 
#    Even closed-source code has access issues because its inevitably and habitually saved to a cvs with different/lower security than the DataStore 
# 2) Its very convenient to change some config settings using the client, without having to deploy modified application code
#    However while some secure data should only be in DataStore, it should not be modifiable in the Client eg Salt  
# Therefore 

PRODUCTION          = os.environ.get('SERVER_SOFTWARE', '').startswith('Google App Eng')
DEVELOPMENT         = not PRODUCTION
APPLICATION_ID      = app_identity.get_application_id()
CURRENT_VERSION_ID  = os.environ.get('CURRENT_VERSION_ID')
CURRENT_VERSION_NAME= CURRENT_VERSION_ID.split('.')[0]

if DEVELOPMENT:
    import calendar
    CURRENT_VERSION_TIMESTAMP = calendar.timegm(datetime.utcnow().timetuple())
else:
    CURRENT_VERSION_TIMESTAMP = long(CURRENT_VERSION_ID.split('.')[1]) >> 28

CURRENT_VERSION_DATE = datetime.utcfromtimestamp(CURRENT_VERSION_TIMESTAMP)

EmailRegEx = util.getEmailRegex()
  
# 
from model.config import Config # NB The model module needs to be imported *after* setting CURRENT_VERSION_TIMESTAMP,
            # since model.ndbModelBase uses it as default value for version_r property
CONFIG_DB   = Config.get_master_db()
SECRET_KEY  = CONFIG_DB.flask_secret.encode('ascii')
#model.AuthProvider.init()

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

class TwoWayDict(dict):
    def __setitem__(_s, key1, key2):
        # Remove any previous connections with these keys
        if not key1.endswith(':'):
            raise ValueError
        if key1 in _s:
            raise ValueError
        if key2 in _s:
            raise ValueError
        dict.__setitem__(_s, key1, key2)
        dict.__setitem__(_s, key2, key1)


authNames = TwoWayDict()
authNames ['_e:'] = '_email'
authNames ['_u:'] = '_userName'

    # OAuth 1.0a
authNames ['bb:'] = 'bitbucket'
authNames ['fk:'] = 'flickr'
authNames ['pk:'] = 'plurk'
authNames ['tt:'] = 'twitter'
authNames ['tb:'] = 'tumblr'
    # 'ubuntuone',  # UbuntuOne service is no longer available
authNames ['vm:'] = 'vimeo'
authNames ['xr:'] = 'xero'
authNames ['xg:'] = 'xing'
authNames ['yh:'] = 'yahoo'

    # OAuth 2.0
authNames ['am:'] = 'amazon'
    # 'behance',  # doesn't support third party authorization anymore.
authNames ['bl:'] = 'bitly'
authNames ['dv:'] = 'deviantart'
authNames ['fb:'] = 'facebook'
authNames ['fs:'] = 'foursquare'
authNames ['gg:'] = 'google'
authNames ['gh:'] = 'github'
authNames ['li:'] = 'linkedin'
authNames ['pp:'] = 'paypal'
authNames ['rd:'] = 'reddit'
authNames ['vk:'] = 'vk'
authNames ['wl:'] = 'windowslive'
authNames ['ym:'] = 'yammer'
authNames ['yd:'] = 'yandex'
authNames ['ig:'] = 'instagram' # not yet impl in authomatic
 
   # OpenID
authNames ['ol:'] = 'openid_livejournal'
authNames ['ov:'] = 'openid_verisignlabs'
authNames ['ow:'] = 'openid_wordpress'
authNames ['oy:'] = 'openid_yahoo'



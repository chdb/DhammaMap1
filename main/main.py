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
# app = flask.Flask(__name__) # pylint: disable=invalid-name
# note:Flask server doesn't need DEBUG parameter while developing, since server restarting is taken care by GAE SDK


# class Config(object):
    # DEVELOPMENT = util.DEVT
    # SECRET_KEY  = util.randomB64()
    # CONFIG_DB = Config.get_master_db()

# config = { 'CONFIG_DB'   : Config.get_master_db().toDict()
         # , 'DEVELOPMENT' : util.DEVT
         # }
# app.config.from_object(config)
    
# util.debugDict(config,'my config ')
# util.debugDict(app.config,'flask app config ')

# app.jinja_env.line_statement_prefix = '#'
# app.jinja_env.line_comment_prefix  = '##'

#import auth # pylint: disable=unused-import
# import control.error
# import control.index
# import control.user
# import model # pylint: disable=unused-import
# import task # pylint: disable=unused-import
#from api import helpers

#API = helpers.Api(app)

# import api.v1 # pylint: disable=unused-import
import logging

logging.debug('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@  main  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')

#logging.debug('####################################################### app id: %r '         , config.APPLICATION_ID)
# logging.debug('####################################################### cur ver id: %r'      , config.CURRENT_VERSION_ID)
# logging.debug('####################################################### cur ver name: %r'    , config.CURRENT_VERSION_NAME)
# logging.debug('####################################################### cur ver timestamp: %r',config.CURRENT_VERSION_TIMESTAMP)
#logging.debug('####################################################### cur ver datetime: %r', config.CURRENT_VERSION_DATE)


# shorts = [i for i[0] in config.authProviders]
# longs  = [i for i[1] in config.authProviders]
# assert len(shorts) == len(set(shorts)), 'no short duplicates' 
# assert len(longs ) == len(set(longs )), 'no long  duplicates'
#import os
#import sys
#import config as myConfig
#import session

# Third party libraries path must be findable before importing webapp2
#sys.path.insert(0, os.path.join (os.path.dirname(__file__), 'Libs'))
import handlers as h
import webapp2

def route (s, hm=None, ms=None, **ka): 
    def route2 (u, H=None, name=None,  hm=None, ms=None, **ka): 
        logging.debug ('route = %s,%s,%s',u, H, name )
        return webapp2.Route (u, H, name, handler_method=hm, methods=ms, **ka)
    
    assert not s.startswith('/') 
    assert not s.endswith('/') 
    assert not ('handler' in ka 
               and 'name' in ka )
    
    u = '/' + s.lower() # u := uri OR uri template
    # if s[-1].isdigit():
        # s = s[:-1]           
    name = re.sub( r'/|-', '', s) # remove '/' and '-'
    p =  re.match( r'<(.+):?.*>', '', name) # find groups parenthized by < : >
    if p:
        name += '_' + p.group(1) # append the first find
    if 'handler' in ka:
        return route2 (u, name, hm=hm, ms=ms, **ka)
    H = eval('handlers.H_'+ name) # H := handler class
    if 'name' in ka:
        return route2 (u, H, hm=hm, ms=ms, **ka)
    return route2 (u, H, name, hm=hm, ms=ms, **ka)

    
rts=[ webapp2.Route('/_ah/warmup', handler=h.H_warmup, name='wu')
    , webapp2.Route('/'          , handler=h.H_home, name='Home')
    ]
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
cfg = config.init()
app = webapp2.WSGIApplication( rts
                             , debug =cfg['development']
                             , config=cfg
                             )
#    session.loadConfig(wa)   # override/add-to  session config defaults with myConfig               
#    logging.debug('config = %r', a.config)

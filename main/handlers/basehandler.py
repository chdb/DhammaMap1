import webapp2 as wa2
from jinja_env import Jinja
import util
import logging

#import model.user as users
from model.config import CONFIG_DB
import config
import validators

def getFlashMessages(): return None

class H_Base (wa2.RequestHandler):

    def __init__(_s, request, response):
        _s.initialize(request, response)
 #       _s.view = ViewClass()
 #       _s.localeStrings = i.getLocaleStrings(_s) # getLocaleStrings() must be called before setting path_qs in render_template()

    def serve (_s, filename, **ka):
        ka['user'      ] = None # _s.user
    #    ka['locale_strings'] = _s.localeStrings
     #   ka['app_config'] = CONFIG_DB.toDict(not auth.is_admin())
        ka['authNames' ] = config.authNames
        ka['validators'] = validators.to_dict(validators)    
        ka['request'   ] = { 'host'     : _s.request.host
                           , 'host_url' : _s.request.host_url
                           }
        ka['get_flashed_messages'] = getFlashMessages   
       # ka['config'] = CONFIG_DB.toDict()   
        
        # logging.debug('***********************************')
        # logging.debug('***********************************')
        # logging.debug('***********************************')
        # logging.debug('***********************************')
        # logging.debug(json.dumps( ka['request']))
        # logging.debug('***********************************')
        # logging.debug('***********************************')
        # logging.debug('***********************************')
        # logging.debug('***********************************')
        
        ka['current_user_isAdmin_'] = True
   #     ka['current_user'] = {'isAdmin_':True}
        util.debugDict(ka, 'params')
        _s.response.write (Jinja().render (filename, ka))

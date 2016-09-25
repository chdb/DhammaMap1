# coding: utf-8
"""
Global config variables. Config variables stored in DB are loaded into CONFIG_DB variable
"""
import os
from datetime import datetime
from google.appengine.api import app_identity #pylint: disable=import-error
import util
import logging 

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


# It is simple and convenient to create some configuration data here in the config file 
# but other config data is stored in ndb DataStore because
# 1) This is not a secure location for cryptographic keys and other secrets because our code base is open-source 
#    Even closed-source code has access issues because its inevitably and habitually saved to a cvs with different/lower security than the DataStore 
# 2) Its very convenient to change config settings without having to deploy modified application code
  
# 
from model.config import Config # NB The model module needs to be imported *after* setting CURRENT_VERSION_TIMESTAMP,
            # since model.ndbModelBase uses it as default value for version_r property
CONFIG_DB   = Config.get_master_db()
SECRET_KEY  = CONFIG_DB.flask_secret.encode('ascii')
#model.AuthProvider.init()



logging.debug('####################################################### app id: %r ', APPLICATION_ID)
logging.debug('####################################################### cur ver id: %r', CURRENT_VERSION_ID)
logging.debug('####################################################### cur ver name: %r', CURRENT_VERSION_NAME)
logging.debug('####################################################### cur ver timestamp: %r', CURRENT_VERSION_TIMESTAMP)
logging.debug('####################################################### cur ver datetime: %r', CURRENT_VERSION_DATE)


# coding: utf-8
"""
Global config variables. Config variables stored in DB are loaded into CONFIG_DB variable
"""
import os
from datetime import datetime
from google.appengine.api import app_identity #pylint: disable=import-error
import util

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


import model        # NB The model module needs to be imported *after* setting CURRENT_VERSION_TIMESTAMP,
                    # since model.ndbModelBase uses it as default value for version property
CONFIG_DB           = model.Config.get_master_db()
SECRET_KEY          = CONFIG_DB.flask_secret.encode('ascii')

import logging 
logging.debug('####################################################### app id: %r ', APPLICATION_ID)
logging.debug('####################################################### cur ver id: %r', CURRENT_VERSION_ID)
logging.debug('####################################################### cur ver name: %r', CURRENT_VERSION_NAME)
logging.debug('####################################################### cur ver timestamp: %r', CURRENT_VERSION_TIMESTAMP)
logging.debug('####################################################### cur ver datetime: %r', CURRENT_VERSION_DATE)
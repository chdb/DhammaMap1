# coding: utf-8
"""
Initializes flask server and assigns all routes by importing modules
"""
import flask
#import config
import util
from model.config import Config # NB The model module needs to be imported *after* setting CURRENT_VERSION_TIMESTAMP,
            # since model.ndbModelBase uses it as default value for version_r property

app = flask.Flask(__name__) # pylint: disable=invalid-name
# note:Flask server doesn't need DEBUG parameter while developing, since server restarting is taken care by GAE SDK


#SECRET_KEY  = CONFIG_DB.flask_secret.encode('ascii')
#model.AuthProvider.init()

class Config(object):
    DEVELOPMENT = util.DEVT
    SECRET_KEY  = util.randomB64()
    CONFIG_DB = Config.get_master_db()

config = Config()
app.config.from_object(config)

util.debugDict(config,'my config ')

util.debugDict(app.config,'flask app config ')


app.jinja_env.line_statement_prefix = '#'
app.jinja_env.line_comment_prefix  = '##'

import auth # pylint: disable=unused-import
import control.error
import control.index
import control.user
import model # pylint: disable=unused-import
import task # pylint: disable=unused-import
from api import helpers

API = helpers.Api(app)

import api.v1 # pylint: disable=unused-import
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

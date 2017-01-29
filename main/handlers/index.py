# coding: utf-8
"""
Injects data for rendering index template - see base.html
"""
import flask
from main import app
import auth
import model.user as users
from model.config import CONFIG_DB
import config
import validators
import util
import logging

@app.route('/')
def index():
    """Render index template"""
    return flask.render_template('index.html')


@app.context_processor
def inject_user():
    """Inject 'user' variable into jinja template, so it can be passed into angular. See base.html"""
    user = False
    if auth.is_logged_in():
        user = auth.currentUser().toDict(publicOnly=False)
    util.debugDict(user, "auth.currentUser" )
    logging.debug('inject user')
    return { 'user': user }


@app.context_processor
def inject_config():
    """Inject 'app_config' variable into jinja template, so it can be passed into angular. See base.html"""
    #config_properties = Config.get_all_properties() if auth.is_admin() else Config.get_public_properties()
    app_config = CONFIG_DB.toDict(not auth.is_admin())
    logging.debug('inject config')
    return { 'app_config': app_config 
           , 'authNames' : config.authNames
           }


@app.context_processor
def inject_validators():
    """Inject vdr-specifiers for regex and min-max validators into jinja template for the client. See base.html
    This is so that client and server can both recreate same ie functionally equivalent validators. 
    However custom validators cannot be passed but generally these are only applied server side
    """
    logging.debug('inject valid')
    return { 'validators' : validators.to_dict(validators) }

           
@app.route('/_ah/warmup')
def warmup():
    """Warmup request to load application code into a new instance before any live requests reach that instance.
    For more info see GAE docs"""
    return 'success'

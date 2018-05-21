#!/usr/bin/python
# -*- coding: utf-8 -*-
#from __future__ import unicode_literals

#import webapp2 as wa2
from webapp2_extras import jinja2
#import session
#import util
from config import appCfg
#import logging
#import json

# def generate_csrf_token():
    # session = wa2.get_request().registry['session']
    # t = session.get('_csrf_token')
    # if not t:
        # t = utils.newToken()
        # session['_csrf_token'] = t
    # return t

def bAutoescape(filename):
    ''' whether to auto-escape the template values - based on the file-extension'''
    if filename:
        n = filename.rfind('.') + 1
        if n:
            ext = filename[n:]
            return ext in('html', 'htm', 'xml')
    return False

class Jinja(object):

    def __init__(_s):
        # instance is cached -  factory is used only if nothing in app-registry at key: 'webapp2_extras.jinja2'
        _s.instance = jinja2.get_jinja2(_s._jinja2_factory)

    @staticmethod
    def _jinja2_factory(app):
        cfg = {}
        cfg['environment_args'] = { 'line_statement_prefix' : '#'
                                  , 'line_comment_prefix'   : '##'
                                  , 'autoescape' : bAutoescape
                                  }

        j = jinja2.Jinja2(app, cfg)
        # see http://jinja.pocoo.org/docs/dev/api/#high-level-api
        # j.environment.autoescape=bAutoescape        # overrides True, set in webapp2_extras.jinja2
        # j.environment.filters.update({  # Set filters  ...
                                    #  })
        j.environment.globals.update({ 'config' : appCfg.toDict() #{'config':}
                                     # , 'uri_for': wa2.uri_for
                                     # , 'csrf_token': generate_csrf_token
                                     # , 'getattr': getattr
                                     })
        j.environment.tests.update ({  # Set test  ...
                                     })
        #util.debugDict(j.environment.globals, 'globals')
        # logging.debug('***********************************')
        # logging.debug('***********************************')
        # logging.debug('***********************************')
        # logging.debug('***********************************')
        # logging.debug(json.dumps( app.config  ))
        # logging.debug('***********************************')
        # logging.debug('***********************************')
        # logging.debug('***********************************')
        # logging.debug('***********************************')

        return j

    def render(_s, template, params):
        return _s.instance.render_template(template, **params)

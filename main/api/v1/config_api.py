# coding: utf-8
# pylint: disable=too-few-public-methods, no-self-use, missing-docstring, unused-argument
from flask_restful import Resource

from main import API
from flask import request
from config import CONFIG_DB
from model import Config
import util
from api.helpers import ok
from api.decorators import admin_required#, model_by_key
import logging

@API.resource('/api/v1/config') #/<string:key>
class AdminConfigAPI(Resource):
    @admin_required
    def get(self):
        return CONFIG_DB.toDict(all=True)

    @admin_required
    #@model_by_key
    def put(self):#, key):
        #logging.debug('key = %s',key)
        if 'recaptcha_forms' in request.json:
            request.json['recaptcha_forms'] = util.dict_to_list(request.json['recaptcha_forms'])
        CONFIG_DB.populate(**request.json)
        CONFIG_DB.put()
        return ok()

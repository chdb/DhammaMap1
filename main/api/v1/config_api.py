# coding: utf-8
# pylint: disable=too-few-public-methods, no-self-use, missing-docstring, unused-argument
from flask_restful import Resource

from main import API
from flask import request
from model.config import CONFIG_DB
#from model import Config
import util
from api.helpers import ok
from api.decorators import admin_required
import logging

@API.resource('/api/v1/config') 
class AdminConfigAPI(Resource):
    @admin_required
    def get(self):
        return CONFIG_DB.toDict(nullVals=True)

    @admin_required
    def put(self):#, key):
        CONFIG_DB.populate(request.json)
        CONFIG_DB.put()
        return ok()

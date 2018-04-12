# coding: utf-8
# pylint: disable=too-few-public-methods, no-self-use, missing-docstring, unused-argument
# from flask_restful import Resource

# from main import API
# from flask import request
from config import appCfg
#from model import MConfig
#import util
#from handlers.api.helpers import ok
from handlers.api.decorators import adminOnly
#import logging
from handlers.basehandler import HAjax
#from config import getInstances
from app import app

@app.API_1('config') 
class HConfig(HAjax):
   
    @adminOnly
    def get(_s):
        return appCfg.toDict(nullVals=True)
        
    @adminOnly
    def put(_s):
        #todo in production we need multi instance code
        #   insts = getInstances()
        #   thisInst = getThisInstance()
        #   for i in insts:
        #       if i != thisInst:
        #           i.send(url=put2each, data=_s.request.body)      
        appCfg.populate(_s.request.json)    
   
    def put2each(_s):
        appCfg.update(_s.json())

# coding: utf-8
# pylint: disable=too-few-public-methods, no-self-use, missing-docstring, unused-argument
from flask_restful import Resource
from main import API
from flask import abort
from config import DEVELOPMENT
#from model.factories import UserFactory
#from factory.fuzzy import FuzzyText, FuzzyChoice
import random
#import factory
import util
from model.user import User
from google.appengine.ext import ndb #pylint: disable=import-error
from api.helpers import ok
import logging

@API.resource('/api/v1/generate_database')
class GenerateDatabaseAPI(Resource):
    @ndb.toplevel
    def post(self):
        """Deletes all users and re-generates mock users for development purposes"""
        if not DEVELOPMENT:
            abort(404) # very important - we dont want to offer users the opportunity to destroy our entire user base
       
        def delete_all():
            ndb.delete_multi(User.query().fetch(keys_only=True))
            
        def create_admin():
            admin = User( username   ='admin'
                        , pwdhash__  =util.password_hash('123456')
                        , isAdmin_   =True
                        , isVerified_=True
                        , isActive_  =True
                        )
            User.put(admin)

        def create_user(n):
            
            def optRandB64():
                return util.randomB64() if random.choice((True, False)) else None
                
            user = User ( username   ='tutshka%d' % n 
                        , pwdhash__  =util.password_hash('123456')
                        , isAdmin_   =False
                        , isVerified_=random.choice((True, False))
                        , isActive_  =random.choice((True, False))
                        , bio        =random.choice(('All component', 'things are', 'impernanent: work', 'out your', 'own salvation', 'with diligence.'))
                        , facebook   =optRandB64()
                        , twitter    =optRandB64()
                        , gplus      =optRandB64()
                        , instagram  =optRandB64()
                        , linkedin   =optRandB64()
                        , github     =optRandB64()
                        )
            User.put(user)
        
        delete_all()
        for n in xrange(45):
            create_user(n)
        create_admin()
        
        return ok()

        
    
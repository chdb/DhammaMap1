# coding: utf-8
# pylint: disable=too-few-public-methods, no-self-use, missing-docstring, unused-argument
from flask_restful import Resource
from main import API
from flask import abort
import util #import DEVELOPMENT
import random
from security import pwd
import model.user as u
from google.appengine.ext import ndb #pylint: disable=import-error
from api.helpers import ok
import logging

@API.resource('/api/v1/generate_database')
class GenerateDatabaseAPI(Resource):
    @ndb.toplevel
    def post(self):
        """Deletes all users and re-generates mock users for development purposes"""
        if not util.DEVT:
            abort(404) # very important - dont give users the opportunity to destroy our entire user base
       
        def delete_all():
            ndb.delete_multi(u.User  .query().fetch(keys_only=True))
            ndb.delete_multi(u.AuthId.query().fetch(keys_only=True))
            
        def create_admin():
            u.User.create ( username   ='admin'
                          , email_     ='admin@xyz.com' 
                          , pwdhash__  =pwd.encrypt('123456')
                          , isAdmin_   =True
                          , isVerified_=True
                          , isActive_  =True
                          , authIds    =u.randomAuthIds()
                          )
            #User.put(admin)

        def create_user(n):
            name = 'tutshka%d' % n 
            u.User.create ( username   =name
                          , email_     =name+'@xyz.com'
                          , pwdhash__  =pwd.encrypt('123456')
                          , isAdmin_   =False
                          , isVerified_=random.choice((True, False))
                          , isActive_  =random.choice((True, False))
                          , bio        =random.choice(('All component', 'things are', 'impermanent: work', 'out your', 'own salvation', 'with diligence.'))
                          , authIds    =u.randomAuthIds()
                          )
            #u.addRandomAuthIds()
            #User.put(usr)
        
        delete_all()
        NumUsers = 15
        for n in xrange(NumUsers):
            create_user(n)
        create_admin()
        return ok()

        
    
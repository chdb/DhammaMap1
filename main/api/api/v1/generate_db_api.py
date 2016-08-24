# coding: utf-8
# pylint: disable=too-few-public-methods, no-self-use, missing-docstring, unused-argument
from flask_restful import Resource
from main import API
from flask import abort
from config import DEVELOPMENT
from model.factories import UserFactory
from google.appengine.ext import ndb #pylint: disable=import-error
from api.helpers import empty_ok_response

@API.resource('/api/v1/generate_database')
class GenerateDatabaseAPI(Resource):
    @ndb.toplevel
    def post(self):
        """Generates mock data for testing"""
        if not DEVELOPMENT:
            abort(404)
        UserFactory.create_batch(5)
        return empty_ok_response()

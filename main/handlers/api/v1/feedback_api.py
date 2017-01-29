# coding: utf-8
# pylint: disable=too-few-public-methods, no-self-use, missing-docstring, unused-argument
from flask_restful import reqparse, Resource
from flask import abort
from main import API
import task
from model.config import CONFIG_DB
from api.helpers import ok, rqArg, rqParse
from api.decorators import verify_captcha
import validators as vdr


@API.resource('/api/v1/feedback')
class FeedbackAPI(Resource):
    
    @verify_captcha('feedbackForm')
    def post(self):
        """Sends feedback email to admin"""
        if not CONFIG_DB.admin_email_:
            return abort(418)
        
        args = rqParse( rqArg('message', vdr=vdr.feedback_span, required=True)
                      , rqArg('fromEma', vdr=vdr.email_rx)
                      )
        MaxSubjLen = 50  # Construct Subject from first MaxSubjLen chars of message. Adjust this if you want.            
        if len(args.message) > MaxSubjLen:
            subject ='%s...' % args.message[:(MaxSubjLen-3)].strip()
        else:
            subject = args.message.strip()
        
        ka = {'reply_to': args.fromEma} if args.fromEma else {}
        task.sendEmail( subject
                      , body= '%s\n\nfrom: %s' % (args.message, args.fromEma)
                      , subjTag='Feedback'
                      , **ka
                      )
        return ok()

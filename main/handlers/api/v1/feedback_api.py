# coding: utf-8
# pylint: disable=too-few-public-methods, no-self-use, missing-docstring, unused-argument
# from flask_restful import reqparse, Resource
# from flask import abort
# from main import API
import task
from config import appCfg
#from handlers.api.helpers import ok#, rqParse
from handlers.api.decorators import verify_captcha
import validators as vdr
from handlers.basehandler import HBase

# @API.resource('/api/v1/feedback')
class FeedbackAPI(HBase):
    
    @verify_captcha('feedbackForm')
    def post(_s):
        """Sends feedback email to admin"""
        if not appCfg.admin_email_:
            return _s.abort(418)
        
        args = args = _s.parseJson(('message', vdr.feedback_span)
                                  ,('fromEma', vdr.email_rx)
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

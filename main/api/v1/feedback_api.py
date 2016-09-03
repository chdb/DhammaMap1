# coding: utf-8
# pylint: disable=too-few-public-methods, no-self-use, missing-docstring, unused-argument
from flask_restful import reqparse, Resource
from flask import abort
from main import API
import task
import config
from api.helpers import ArgVdr, empty_ok_response, rqArg, rqParse
from api.decorators import verify_captcha
from model import UserVdr


@API.resource('/api/v1/feedback')
class FeedbackAPI(Resource):
    
    @verify_captcha('feedbackForm')
    def post(self):
        """Sends feedback email to admin"""
        if not config.CONFIG_DB.admin_email_:
            return abort(418)
        
        # p = reqparse.RequestParser()
        # p.add_argument('message', type=ArgVdr.fn('feedback'), required=True)     #this 'required' is for add_argument()
        # p.add_argument('email', type=UserVdr.fn('email_rx', required=False))  #this 'required' is for fn()
        # args = p.parse_args()
        args = rqParse( rqArg('message', argVdr='feedback_span', required=True)
                      , rqArg('fromEma', userVdr=('email_rx', False))
                      )
        MaxSubjLen = 50              
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
        return empty_ok_response()

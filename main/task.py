# coding: utf-8
"""
Module for created app engine deferred tasks. Mostly sending emails
"""
import logging
#import flask
from google.appengine.api import mail #pylint: disable=import-error
from google.appengine.ext import deferred #pylint: disable=import-error
from config import appCfg
import util
import webapp2 as wa2
from signup_q import Midstore


def sendEmail(subject, body, toEma=None, subjTag=None, **ka):
    """send email using GAE's mail and deferred modules
    Args  : subject (string)            : Email subject
            body    (string)            : Email body
            toEma   (string, optional)  : Email to, if omitted will send email to admin ema
            **kwargs                    : Arbitrary keyword arguments.
    """
    if appCfg.admin_email_:
        site_name = appCfg.site_name
        adminEma  = '%s <%s>' % (site_name, appCfg.admin_email_)
        toEma = toEma or adminEma
        subject = '[%s: %s] %s' % (site_name, subjTag, subject) if subjTag else\
                  '[%s] %s'     % (site_name, subject)
        
        if appCfg.development:
            logging.info( '\n######### Deferring to send this email: #############################'
                          '\nFrom: %s'
                          '\nTo: %s'
                          '\nSubject: %s'
                          '\n'
                          '\n%s'
                          '\n#####################################################################'
                          '\n'
                          , adminEma # from ema
                          , toEma
                          , subject
                          , body
                          )
        #todo - shouldn't we use the task queue here - perhaps for more control of max rate of sending
        deferred.defer  ( mail.send_mail
                        , adminEma # from ema
                        , toEma
                        , subject
                        , body
                        , **ka)


def sendNewUserEmail(usr):
    """Sends notification to admin about newly registered user, iff notify_on_new_user_ is true in config database
    Args :  usr (model.User): newly registered user
    """
    url = '%s#!/user/%s' % (wa2.uri_for('home', _full=True), usr.email_)
    body = ('New User Signed Up'
            '\nname: %s'
            '\nemail: %s'
        #    '\n%s'
            '\nurl: %s' 
             %  ( usr.name
                , usr.email_
         #       , '\n'.join([': %s' % a for a in usr.authIds])
                , url
           )    )
    subj = 'New user: %s' % usr.name
    sendEmail(subj, body)

    
def sendResetEmail(usr):
    """Sends email with url, which user can use to reset his password
    Args : usr (model.User): User, who requested password reset
    """
    if not usr.email_:
        return
    usr.token__ = util.randomB64()
    usr.put()

    toEma = '%s <%s>' % (usr.name, usr.email_)
    body = reset_text % { 'name': usr.name
                        , 'link': wa2.uri_for('user_reset', token=usr.token__, _full=True)
                        , 'siteName': appCfg.site_name
                        }
    sendEmail('Reset your password', body, toEma)

def sendVerifyEmail(ema, nonce, tag):
    """Sends email, which user can use to verify his email address
    Args :  usr (model.User): user, who should verify his email
    """
    # logging.debug('vvvvvvvvvvvvvvvvvvv')
    # ema = usr.pop('email_')
    #uname = usr.pop('username')
    #assert usr == {}
         
    # nonce = util.randomB64(appCfg.NonceBYTES)
    # tag = Midstore('SignupQ').put(nonce, ema, usr.name)

    # usr.token__ = util.randomB64()
    # usr.put()
    
    logging.debug('wtoken = %r', nonce+tag)
    uri = wa2.uri_for('home', _full=True) + '#!/verify/' + nonce + tag
    body = verify_text % {'link'    : uri
                         ,'siteName': appCfg.site_name
                         }
    sendEmail('Please verify your email', body, toEma=ema)


# -----------------------------------------------------------
reset_text =\
'''Hello %(name)s,
We understand that you want to reset your password at %(siteName)s.
In that case, please follow this link:

    %(link)s
    
The old password will remain valid until you click the link. 

Sometimes people people can recieve these emails in error.So, if you dont want to reset your password, we apologize. you can ignore this email.
For example because someone was playing around to test our security. But don't be alarmed:this link was sent only to you so there is no security breach. 
You can delete this email, but first please can you reply to it, with or without some explanation so we can take a look and see what happened.

Best regards,
%(siteName)s
''' 
# --------------------------------------------------------
verify_text =\
'''Welcome to %(siteName)s.
Please click the link below to confirm your email address and activate your account:

    %(link)s

If it wasn't you, we apologize. You can ignore this email, but its better if you reply to it
so we can take a look.
Best regards,
%(siteName)s
'''
# -----------------------------------------------------

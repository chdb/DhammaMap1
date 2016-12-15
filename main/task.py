# coding: utf-8
"""
Module for created app engine deferred tasks. Mostly sending emails
"""
import logging
import flask
from google.appengine.api import mail #pylint: disable=import-error
from google.appengine.ext import deferred #pylint: disable=import-error
from model.config import CONFIG_DB
import util


def sendEmail(subject, body, toEma=None, subjTag=None, **ka):
    """send email using GAE's mail and deferred modules
    Args  : subject (string)            : Email subject
            body    (string)            : Email body
            toEma   (string, optional)  : Email to, if omitted will send email to admin ema
            **kwargs                    : Arbitrary keyword arguments.
    """
    if CONFIG_DB.admin_email_:
        site_name = CONFIG_DB.site_name
        adminEma  = '%s <%s>' % (site_name, CONFIG_DB.admin_email_)
        toEma = toEma or adminEma
        subject = '[%s: %s] %s' % (site_name, subjTag, subject) if subjTag else\
                  '[%s] %s'     % (site_name, subject)
        
        if util.DEVT:
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
    url = '%s#!/user/%s' % (flask.url_for('index', _external=True), usr.username)
    body = ('\nusername: %s'
            '\nemail: %s'
            '\n%s'
            '\nurl: %s' 
             %  ( usr.username
                , usr.email_
                , '\n'.join([': %s' % a for a in usr.authIds])
                , url
           )    )
    sendEmail('New user: %s' % usr.username, body)

    
def sendResetEmail(usr):
    """Sends email with url, which user can use to reset his password
    Args : usr (model.User): User, who requested password reset
    """
    if not usr.email_:
        return
    usr.token__ = util.randomB64()
    usr.put()

    toEma = '%s <%s>' % (usr.username, usr.email_)
    body = reset_text % { 'name': usr.username
                        , 'link': flask.url_for('user_reset', token=usr.token__, _external=True)
                        , 'siteName': CONFIG_DB.site_name,
                        }
    sendEmail('Reset your password', body, toEma)


def sendVerifyEmail(usr):
    """Sends email, which user can use to verify his email address
    Args :  usr (model.User): user, who should verify his email
    """
    if not usr.email_:
        logging.info ('no email address for sending')
        return
    usr.token__ = util.randomB64()
    usr.put()

    toEma = usr.email_
    body = verify_text % { 'link': flask.url_for('user_verify', token=usr.token__, _external=True)
                         , 'siteName': CONFIG_DB.site_name,
                         }
    sendEmail('Verify your email', body, toEma)


# -----------------------------------------------------------
reset_text =\
'''Hello %(name)s,
It seems someone tried to reset your password with %(siteName)s.
Hopefully it was from you! In that case, please reset it by following this link:

%(link)s

If it wasn't you, we apologize. Don't be alarmed: there is no security breach because this email was sent only to you 
- no one else has a copy of it.  You can delete this email, but its better if you reply to it so we can take a look.
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

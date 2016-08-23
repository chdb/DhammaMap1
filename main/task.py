# coding: utf-8
"""
Module for created app engine deferred tasks. Mostly sending emails
"""
import logging
import flask
from google.appengine.api import mail #pylint: disable=import-error
from google.appengine.ext import deferred #pylint: disable=import-error
import config
import util


def sendEmail(subject, body, toEma=None, **ka):
    """send email using GAE's mail and deferred modules
    Args  : subject (string)            : Email subject
            body    (string)            : Email body
            toEma   (string, optional)  : Email to, if omitted will send email to admin ema
            **kwargs                    : Arbitrary keyword arguments.
    """
    if config.CONFIG_DB.admin_email_p:
        site_name = config.CONFIG_DB.site_name
        adminEma  = '%s <%s>' % (site_name, config.CONFIG_DB.admin_email_p)
        toEma = toEma or adminEma
        #fromEma = adminEma
        subject = '[%s] %s' % (site_name, subject)
        
        if config.DEVELOPMENT:
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
        deferred.defer  ( mail.send_mail
                        , adminEma # from ema
                        , toEma
                        , subject
                        , body
                        , **ka)


def sendNewUserEmail(user_db):
    """Sends notification to admin about newly registered user, iff notify_on_new_user_p is true in config database
    Args :  user_db (model.User): newly registered user
    """
    url = '%s#!/user/%s' % (flask.url_for('index', _external=True), user_db.username)
    body = ( 'name: %s'
           '\nusername: %s'
           '\nemail: %s'
           '\n%s'
           '\nurl: %s' % \
                ( user_db.name
                , user_db.username
                , user_db.email_p
                , ''.join([': '.join(('%s\n' % a).split('_')) for a in user_db.authIDs_p])
                , url
           )    )
    sendEmail('New user: %s' % user_db.name, body)

# ##################################################################################################
reset_text =\
'''Hello %(name)s,
It seems someone tried to reset your password with %(brand)s.
Hopefully it was from you! In that case, please reset it by following this link:

%(link)s

If it wasn't you, don't be alarmed. There is no security breach because this email was sent only to you 
- no one else has a copy of it.  You can delete this email or it or reply to it so we can take a look.
Best regards,
%(brand)s
''' 
# ##################################################################################################
verify_text =\
'''Welcome to %(brand)s.
Please click the link below to confirm your email address and activate your account:

%(link)s

If it wasn't you, we apologize. You can either ignore this email or reply to it
so we can take a look.
Best regards,
%(brand)s
'''
# ##################################################################################################
def sendResetEmail(user_db):
    """Sends email with url, which user can use to reset his password
    Args : user_db (model.User): User, who requested password reset
    """
    if not user_db.email_p:
        return
    user_db.token_h = util.uuid()
    user_db.put()

    toEma = '%s <%s>' % (user_db.name, user_db.email_p)
    body = reset_text % { 'name': user_db.name
                        , 'link': flask.url_for('user_reset', token=user_db.token_h, _external=True)
                        , 'brand': config.CONFIG_DB.site_name,
                        }
    sendEmail('Reset your password', body, toEma)


def sendVerifyEmail(user_db):
    """Sends email, which user can use to verify his email address
    Args :  user_db (model.User): user, who should verify his email
    """
    if not user_db.email_p:
        logging.info ('no email')
        return
    user_db.token_h = util.uuid()
    user_db.put()

    toEma = user_db.email_p
    body = verify_text % { 'link': flask.url_for('user_verify', token=user_db.token_h, _external=True)
                         , 'brand': config.CONFIG_DB.site_name,
                         }
    sendEmail('Verify your email', body, toEma)

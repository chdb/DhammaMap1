# coding: utf-8
"""
Provides error handler for non API errors
"""
import logging
# import werkzeug.exceptions as ex
# import flask

from api import helpers
import env
import webapp2

from main import app

# 423 is in latest version of werkzeug but its not yet released
class Locked(ex.HTTPException):
    """*423* `Locked`
    Used if the resource that is being accessed is locked.
    """
    code = 423
    description =('The account is locked.'  )


# flask.abort.mapping.update({ 423: Locked })


# @app.errorhandler(400)  # Bad Request
#@app.errorhandler(401)  # Unauthorized
#@app.errorhandler(403)  # Forbidden
#@app.errorhandler(404)  # Not Found
#@app.errorhandler(405)  # Method Not Allowed
#@app.errorhandler(410)  # Gone
#@app.errorhandler(418)  # I'm a Teapot
# @app.errorhandler(500)  # Internal Server Error
def error_handler(err):
    """If error occured we render index so it can be flashed to screen """
    logging.exception(err)
    try:
        err.code
    except AttributeError:
        err.code = 500
        err.name = 'Internal Server Error'

    if flask.request.path.startswith('/api/'):
        return helpers.handle_error(err)

    # flask.flash(err.name)
    # return flask.render_template('index.html')


if not env.ENV['development']:
    # @app.errorhandler(Exception)
    def production_error_handler(err): # pylint: disable=missing-docstring
        return error_handler(err)

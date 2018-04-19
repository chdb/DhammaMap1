import webapp2 as wa2
from jinja_env import Jinja
import util
import logging
#import json
from model.mUser import MUser
#from model.mConfig import CONFIG_DB

import config
import validators as vdr
#from handlers.api.helpers import rqParse
from session import SessionVw

#def getFlashMessages(): return None #todo
try:  import simplejson as json
except ImportError: import json


class Namespace(dict):
    ''' a dictionary with class attribute interface as an alternative
        EG  >>> ns = Namespace({'abc':123})
            >>> ns['abc'] # as dict
            123
            >>> ns.abc    # as class attribute
            123
    '''
    def __getattr__(_s, name):
        try:
            return _s[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(_s, name, value):
        _s[name] = value


class Required():pass
required = Required()

class Optional():pass
optional = Optional()


class HBase(wa2.RequestHandler):

    def __init__(_s, request, response):
        _s.initialize(request, response)

        # Provide sensible aliases for misleading attribute names "request.GET" "request.POST"
        _s.request.urlData  = _s.request.GET  # data from the uri's query string - url method could be any http verb (not just get)
        _s.request.formData = _s.request.POST # data from the request body as form - url method could be put etc  (not just post)

 #       _s.view = ViewClass()
 #       _s.localeStrings = i.getLocaleStrings(_s) # getLocaleStrings() must be called before setting path_qs in render_template()

    def dispatch(_s):
        try:
        # try:# csrf protection
            if(_s.request.method == "POST"
            and not _s.request.path.startswith('/tq')): # tq indicates a TaskQueue handler: they are internal therefore not required to have csrf token
                ssnTok  = _s.ssn.get('_csrf_token')
                postTok = _s.request.get('_csrf_token')
                if(not ssnTok  # toks differ or if both are the same falsy
                or  ssnTok != postTok):
                    logging.warning('path = %r',_s.request.path)
                    logging.warning('ssn  csrf token = %r',ssnTok)
                    logging.warning('post csrf token = %r',postTok)
                    logging.warning('CSRF attack or bad or missing csrf token?')
  #                  wa2.abort(403) # 'Forbidden'

            rv = wa2.RequestHandler.dispatch(_s) # NB use super if multiple inheritance. Dispatch the request.this is needed for wa2 sessions to work
        finally:
            # u = _s.user
            # if u and u.modified:
                # u.put() # lazy put() to not put user more than once per request
            _s.ssn.save() # Save ssn after every request
        # except: # an exception in TQ handler causes the TQ to try again which loops
            # logging.exception('unexpected exception in dispatch')
        # if isinstance(rv, basestring):
            # rv = webapp2.Response(rv)
        return rv


    # def handle_exception(_s, exception, debug):
        # logging.exception(exception)
        # _s.response.write('Oops! An error occurred.')
        # if isinstance(exception, wa2.HTTPException):
            # _s.response.set_status(exception.code)
        # else:
            # _s.abort(500, detail=str(exception))


    def pageResponse(_s, filename, **ka):
     #   ka['user'      ] = None # _s.user
    #    ka['locale_strings'] = _s.localeStrings
     #   ka['app_config'] = CONFIG_DB.toDict(auth.is_admin())
        ka['authNames' ] = config.authNames
        ka['validators'] = vdr.to_dict(vdr)
        ka['request'   ] = { 'host'     : _s.request.host
                           , 'host_url' : _s.request.host_url
                           }
        ka['get_flashed_messages'] = _s.ssn.getFlashes
       # ka['config'] = CONFIG_DB.toDict()

        ka['current_user_isAdmin_'] = True
   #     ka['current_user'] = {'isAdmin_':True}


        util.debugDict(ka, 'params')
        logging.debug('XXXXXXXXXXXXX')
        _s.response.write(Jinja().render(filename, ka))

    # def respond(_s, d=None): # ajaxResponse
        # '''use this for ajax responses'''
        # if d:
            # d['msgs'] = _s.get_fmessages()
           ## resp = json.dumps(d)
           ## _s.response.write(resp)
            # _s.response.json = d
        # else:
            # assert d is None,'dont pass an empty object to respond()'
            # assert not _s.response.body
            # _s.response.status_int = 204

    # def ok(_s):
        # """Returns OK response with empty body"""
        # _s.response.status_int = 204


    @wa2.cached_property
    def apiName(_s):
        assert _s.__class__.__name__.startswith('H')
        return _s.__class__.__name__[1:]


    def setLock(_s, lockname, duration):
        def lockOn(kStr, mode, usrMsg, logMsg):
            m.Lock.set(kStr, duration)
            _s.flash('Too many %s failures: %s for %s.' %(_s.apiName, usrMsg, util.hoursMins(duration)))
            logging.warning('%s BruteForceAttack! on %s page: %s', mode, _s.apiName, logMsg)
            logging.warning('Start lock on %s: ema:%s pwd:%s ipa:%s', lockname, ema, pwd, ipa)


        logging.debug('xxxxxxxxxxxxxxxxxxxxxxxxxxx LOCK XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
        ipa = _s.request.remote_addr
        ema = _s.request.json['loginId'] # TODO: loginId might not be email address EG a username
        pwd = _s.request.json['password']
        if   lockname == 'ipa':     lockOn(ipa, 'Local'     , 'you are now locked out'    , "repeated bad attempts with same ipa but different ema's")
        elif lockname == 'ema_ipa': lockOn(ema, 'Local'     , 'this account is now locked', "repeated bad attempts with same ema and ipa")
        elif lockname == 'ema':     lockOn(ema, 'Distributed','this account is now locked', "repeated bad attempts with same ema but different ipa's")

        # todo this password stuff is not generic to other handlers
        #pwd = _s.request.get('password')


 #   def json(_s):
#        return json.loads(_s.request.body)

    def parse(_s, dataLoc, *pa, **ka):
        ''' Parse the args from the dataloc of the request, in accordance with tuples supplied, applying a validator to each.
            If there is no request data and no default for a given tuple then return http 400: '"%s" not found in the request data'
            If the request does not have data for a tuple, then the default value is applied if that is given in the tuple.
            Request data that is not in the list of tuples will return http 400:'Unparsed args: %s', unless strict=False is passed to parseArgs.
            The resulting values are returned in Namespace object.

            tuple form: (name, validator, defaultValue)
        '''
        assert dataLoc == 'json' or 'urlData' or 'formData'

        def validate(vdr, val):
            logging.debug('validating val: %r ###################################################################################', val)
            return (vdr(val, **ka) if callable(vdr) else
                    vdr.fn(val, **ka))

        def parseArg(unparsed, name, vdr=None, dflt=required):
            if vdr is None:
                vdr = lambda x:x  # no-op validator: always valid, does not throw
            logging.debug('name : %r',name)
            if name in args:
                if dataLoc == 'json':
                    res[name] = validate(vdr, args[name])
                else:
                    values = args.getall(name)
                    res[name] =( validate(vdr, values[0]) if len(values)==1 else
                                [validate(vdr, v) for v in values] )
            elif dflt is required:
                _s.abort(400, detail='"%s" not found in the request data'%name)
            elif dflt is not optional:
                res[name] = dflt
            #else: this name is not in request but its optional, so do nothing
            if strict:
                if name in unparsed:
                    unparsed.remove(name)
            return res, unparsed

        res = Namespace()
        strict = ka.pop('strict', True)
        logging.debug('urlData: %r', _s.request.urlData)
        logging.debug('formData: %r', _s.request.formData)
        logging.debug('body: %r', _s.request.body)
        args = getattr(_s.request, dataLoc) # IE one of: _s.request.json, _s.request.urlData, _s.request.formData

        #args['captcha'] = '999' #TESTING!!!

        logging.debug('args: %r',args)
        if dataLoc == 'json' and _s.request.content_type != 'application/json':
            _s.abort(400, 'Expecting json content, but received: %s', _s.request.content_type)
        #assert type(args) is dict
        unparsed = args.keys()
        for t in pa:
            logging.debug('tuple t: %r',t)
            res, unparsed = parseArg(unparsed, *t)
        if strict and unparsed:
            _s.abort(400, 'Unparsed args: %s' % str(unparsed))
        return res

    def parseJson(_s, *pa, **ka):
        return _s.parse('json', *pa, **ka)

    def parseUrl(_s, *pa, **ka):
        return _s.parse('urlData', *pa, **ka)

    #@rateLimit
    def credentials(_s):
        """Parses credentials posted by client and loads appropriate user from datastore"""
        return _s.parseJson(('loginId' , vdr.loginId_span)
                           ,('password', vdr.password_span)
                           ,('remember', vdr.toBool, False)
                         #  , strict=False
                           )

    def logIn(_s, user, remember=False):
        logging.debug('$$$$$$$$$$$$$$$$$$$$$')
        _s.ssn.logIn(user, _s.request.remote_addr, remember)
        logging.debug('%%%%%%%%%%%%%%%%%%%%%%%%')

    def logOut(_s):
        return _s.ssn.logOut()

    @property
    def ssn(_s):
        #import traceback
        #logging.debug('@@@@@@@@@ 1 rq registry: %r',_s.request.registry)
        sn = _s.request.registry.get('session')
        if not sn:
            # try:
            sn = SessionVw(_s)
            _s.request.registry['session'] = sn#logging.debug('@@@@@@@@@ 2 rq registry: %r',_s.request.registry)
            # raise RuntimeError
        # except:
            #logging.exception('@@@@@@@@@')
            #stacktrace = ''.join(traceback.format_stack()[-3:])
            #logging.info("TRACE last 3:\n %s", stacktrace)
        return sn

    @wa2.cached_property
    def loggedInUser(_s):
        uid = _s.ssn.get('_userID')
       # logging.debug('xxxxxxxxxx ssn = %r',_s.ssn)
        if uid:
            return MUser.get_by_id(uid)
        return None

    def flash(_s, msg):
        #logging.info('>>>>>>>>>>>>> msg: %r' % msg)
        _s.ssn.addFlash(msg)

    def get_fmessages(_s):
        fmsgs_html = u''
        flist = _s.ssn.getFlashes()
        #logging.info('>>>>>>>>>>>>> ok added fmsgs: %r' % f)
        if flist:
            fmsgsTmpl = Template(  '{%- if fmessages -%}'
                                        '{%- for fmsg in fmessages -%}'
                                            '<li>{{ fmsg.0 }}</li>'
                                        '{%- endfor -%}'
                                    '{%- endif -%}'
                                 )
            fmsgs_html = fmsgsTmpl.render(fmessages=flist) # _s.ssn.getFlashes())
            # logging.info('>>>>>>>>>>>>> ok tmplate fmsgs: %r' % fmsgs_html)
            # logging.info('>>>>>>>>>>>>> ok tmplate fmsgs: %r' %  str(fmsgs_html))
            return util.utf8(fmsgs_html)
        return None
#------------------------------------

class HAjax(HBase):

    def __init__(_s, request, response):
        super(HAjax,_s).__init__(request, response)

    def dispatch(_s):
        rv = super(HAjax,_s).dispatch() # rv is the AJAX response
       # fmsgs = _s.ssn.getFlashes()
        if rv is None:# and fmsgs is None:
            if _s.response.body:
                logging.warning('Body not empty: %r',_s.response.body)
            _s.response.status_int = 204
        else:
            # assert type(rv) is dict,'ajax response has to be jsonifyable'
           # rv['get_flashed_messages'] = _s.get_fmessages()
            try:
                #logging.debug('rv=%r',rv)
                json.loads(rv)          # test whether rv is a json string...
                _s.response.body = rv   # ... yes, no need to jsonify, write directly to body
            except (ValueError, TypeError):
                _s.response.json = rv   # ... no, must use response.json which calls json.dumps() to jsonise rv
        # if isinstance(rv, basestring):
        # rv = webapp2.Response(rv)
      # ka['get_flashed_messages'] = _s.getFlashes()

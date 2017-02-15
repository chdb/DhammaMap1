import webapp2 as wa2
from jinja_env import Jinja
import util
import logging
import json
#import model.user as users
#from model.config import CONFIG_DB
import model.user as user 
import config
import validators as vdr
#from handlers.api.helpers import rqParse
from session import SessionVw

def getFlashMessages(): return None #todo


class Namespace(dict):
    ''' a dictionary with an alternative class attribute interface
        eg  >>> ns = Namespace({'abc':123})
            >>> ns['abc']
            123
            >>> ns.abc
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
    


class HBase (wa2.RequestHandler):

    def __init__(_s, request, response):
        _s.initialize(request, response)
        
        # Provide sensible aliases for misleading attribute names "request.GET" "request.POST"
        # "request.GET"  has data from the uri's query string. Request could have used any HTTP method: GET, POST, PUT etc
        # "request.POST" has data from the request body, IE from any form whether sent with POST or PUT or even CONNECT, OPTIONS or PATCH
        _s.request.uriData  = _s.request.GET  # data could be from any http verb (not just get) 
        _s.request.formData = _s.request.POST # data could be from http put etc   (not just post)  
        
 #       _s.view = ViewClass()
 #       _s.localeStrings = i.getLocaleStrings(_s) # getLocaleStrings() must be called before setting path_qs in render_template()

    def handle_exception(_s, exception, debug):
        logging.exception(exception)
        _s.response.write('Oops! An error occurred.')
        if isinstance(exception, wa2.HTTPException):
            _s.response.set_status(exception.code)
        else:
            _s.response.set_status(500)
            
            
    def pageResponse (_s, filename, **ka):
        ka['user'      ] = None # _s.user
    #    ka['locale_strings'] = _s.localeStrings
     #   ka['app_config'] = CONFIG_DB.toDict(not auth.is_admin())
        ka['authNames' ] = config.authNames
        ka['validators'] = vdr.to_dict(vdr)    
        ka['request'   ] = { 'host'     : _s.request.host
                           , 'host_url' : _s.request.host_url
                           }
        ka['get_flashed_messages'] = getFlashMessages   
       # ka['config'] = CONFIG_DB.toDict()   
                
        ka['current_user_isAdmin_'] = True
   #     ka['current_user'] = {'isAdmin_':True}
   

        util.debugDict(ka, 'params')
        logging.debug('XXXXXXXXXXXXX')
        _s.response.write (Jinja().render (filename, ka))

    def ajaxResponse (_s, **ka):
        '''use this for ajax responses'''
        ka['msgs'] = _s.get_fmessages()
        resp = json.dumps (ka)
        _s.response.write (resp)
        
    @wa2.cached_property
    def apiName (_s):
        assert _s.__class__.__name__.endswith('API')
        return _s.__class__.__name__[:-3]

      
    def setLock (_s, lockname, duration):
        def lockOn (kStr, mode, msg): 
            m.Lock.set (kStr, duration, _s.apiName)
            _s.flash ('Too many %s failures: %s for %s.' % ( _s.apiName, msg, u.hoursMins(duration)))
        
        logging.debug('xxxxxxxxxxxxxxxxxxxxxxxxxxx LOCK XXXXXXXXXXXXXXXX')
        if name == 'ipa': # repeated bad attempts with same ipa but diferent ema's
            lockOn (ipa,'Local','you are now locked out')
        elif name == 'ema_ipa':# repeated bad attempts with same ema and ipa
            lockOn (ema,'Local','this account is now locked')
        elif name == 'ema': # repeated bad attempts with same ema but diferent ipa's
            lockOn (ema,'Distributed','this account is now locked')
        
        # todo this password stuff is not generic to other handlers
        pwd = _s.request.get('password')
        logging.warning('%s BruteForceAttack! on %s page: start lock on %s: ema:%s pwd:%s ipa:%s',mode, hlr, name, ema, pwd, ipa)

    
    def parseJson (_s, *pa, **ka):
                
        def parseArg (unparsed, name, vdr=None, deflt=required):
            #global unparsed
            if vdr is None:
                vdr = lambda x:x  # no-op
            logging.debug('name : %r',name)
            if name in args:
                res[name] = ( vdr(args[name]) if callable(vdr) else
                              vdr.fn(args[name]) )
            # if name in reqLoc:
                # values = reqLoc.getall(name)
                # res[name] = (vdr(values[0])  if len(values)==1 else
                            # [vdr(v) for v in values] )       
            elif deflt is required:
                #logging.debug('args reqLoc: %r', reqLoc)
                _s.abort (400, detail='"%s" not found in the request data'%name)
            elif deflt is not optional:
                res[name] = deflt
            #else: name is not in request but its optional, so do nothing
            if strict:
                if name in unparsed:
                    #unparsed = [a for a in unparsed if a != name]
                    unparsed.remove(name)
                    
            return res, unparsed
            
        res = Namespace()
        strict = ka.get('strict', True)
        args = json.loads(_s.request.body)
        assert type(args) is dict
        unparsed = args.keys()
        logging.debug('body args : %r',args)
        logging.debug('ka: %r',ka)
        for t in pa:
            logging.debug('tuple t: %r',t)
            #logging.debug('args *a: %r',*a)
            res, unparsed = parseArg(unparsed, *t)
     
        if strict and unparsed:
            _s.abort (400, detail='Unexpected unparsed args: %s' % str(unparsed))
        return res
            

    def usrByCredentials (_s):
        """Parses credentials posted by client and loads appropriate user from datastore"""
        logging.debug('uriData: %r', _s.request.uriData)
        logging.debug('formData: %r', _s.request.formData)
        logging.debug('body: %r', _s.request.body)

        a = _s.parseJson(('loginId',  vdr.loginId_span)
                        ,('password', vdr.password_span)
                        ,('remember', vdr.toBool, False)
                        ) 
        return user.byCredentials(a.loginId, a.password) , a.remember


        
    def signIn (_s, user, remember=False):
        logging.debug('$$$$$$$$$$$$$$$$$$$$$')
        _s.ssn.signIn (user, _s.request.remote_addr, remember)
        logging.debug('%%%%%%%%%%%%%%%%%%%%%%%%')
         
    def signOut (_s):
        return _s.ssn.signOut()
        
    @property
    def ssn (_s):
        #import traceback
        #logging.debug ('@@@@@@@@@ 1 rq registry: %r',_s.request.registry)
        sn = _s.request.registry.get('session')
        if not sn:
            # try:
            sn = SessionVw(_s)
            _s.request.registry['session'] = sn#logging.debug ('@@@@@@@@@ 2 rq registry: %r',_s.request.registry)
            # raise RuntimeError
        # except:
            #logging.exception('@@@@@@@@@')
            #stacktrace = ''.join(traceback.format_stack()[-3:])
            #logging.info ("TRACE last 3:\n %s", stacktrace)
        return sn

    @wa2.cached_property
    def user (_s):
        uid = _s.ssn.get('_userID')
        logging.debug('xxxxxxxxxx ssn = %r',_s.ssn)
        if uid:
            return m.User.byUid (uid)
        return None

    def flash(_s, msg):
        #logging.info('>>>>>>>>>>>>> msg: %r' % msg)  
        _s.ssn.addFlash (msg)
         
    def get_fmessages (_s):
        fmsgs_html = u''
        flist = _s.ssn.getFlashes()
        #logging.info('>>>>>>>>>>>>> ok added fmsgs: %r' % f)  
        if flist:
            fmsgsTmpl = Template (  '{%- if fmessages -%}'
                                        '{%- for fmsg in fmessages -%}'
                                            '<li>{{ fmsg.0 }}</li>'
                                        '{%- endfor -%}'
                                    '{%- endif -%}'
                                 )
            fmsgs_html = fmsgsTmpl.render (fmessages=flist) # _s.ssn.getFlashes())
            # logging.info('>>>>>>>>>>>>> ok tmplate fmsgs: %r' % fmsgs_html)  
            # logging.info('>>>>>>>>>>>>> ok tmplate fmsgs: %r' %  str(fmsgs_html))  
        return util.utf8(fmsgs_html)


#------------------------------------

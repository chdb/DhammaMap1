from datetime import datetime
import os
import logging

def initEnv():
    DEVT = not os.environ.get('SERVER_SOFTWARE', '').startswith('Google App Eng')
    VERid = os.environ.get('CURRENT_VERSION_ID')
    VERname = VERid.split('.')[0] if VERid else None

    if DEVT:
        import calendar
        VERtimeStamp = calendar.timegm(datetime.utcnow().timetuple())
    else:
        VERtimeStamp = long(VERid.split('.')[1]) >> 28 if VERid else None
    
    VERdateTime = datetime.utcfromtimestamp(VERtimeStamp).strftime("%Y-%m-%d %H:%M:%S")
    
    logging.debug('####################################################### cur ver id: %r'      , VERid)
    logging.debug('####################################################### cur ver name: %r'    , VERname)
    logging.debug('####################################################### cur ver timestamp:%r', VERtimeStamp)
    logging.debug('####################################################### cur ver datetime: %r', VERdateTime)
    return  { 'development' : DEVT
            , 'CURRENT_VERSION_ID' : VERid
            , 'CURRENT_VERSION_NAME' : VERname
            , 'CURRENT_VERSION_TIMESTAMP' : VERtimeStamp
            , 'CURRENT_VERSION_DATE' : VERdateTime
            }

logging.debug('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ LOADING ENV')
ENV = initEnv()

# not needed
# _env_ = None

# def env(key=None):
    # def getEnv():
        # global _env_    
        # if _env_:
            # return _env_------------------------------
        # _env_ = initEnv()
        # return _env_
        
    # if key:
        # return getEnv()[key]
    # return getEnv()
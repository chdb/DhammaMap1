# non-api handlers
import handlers.basehandler as bh
import logging
from app import app

@app.route('', name='home' )
class HHome(bh.HBase):

    def get(_s):
        """Render index template"""
        u = _s.loggedInUser
        _s.pageResponse('index.html', user=u.toDict() if u else None )


@app.route('_ah/warmup', name='warmup')
class HWarmup(bh.HBase):

    def get(_s):
        """Warmup request to load application code into a new instance before any live requests reach that instance.
        For more info see GAE docs"""
        logging.debug('self2 = %r',_s)
        _s.response.headers['Content-Type'] = 'text/plain'
        _s.response.write('Warmup successful')

logging.info('QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ')

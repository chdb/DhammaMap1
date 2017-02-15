# non-api handlers
import basehandler as bh

class H_home (bh.HBase):
    def get(_s):
    #def index():
        """Render index template"""
        _s.pageResponse ('index.html')

           
class H_warmup (bh.HBase):
    def get(_s):
        """Warmup request to load application code into a new instance before any live requests reach that instance.
        For more info see GAE docs"""
        _s.response.headers['Content-Type'] = 'text/plain'
        _s.response.write('Warmup successful')
        

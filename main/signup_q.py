 
# We save the signup token and signup data here until the email is verified.
# For monitoring sometimes we might want to review how many users dont complete the signup, process 
# Also we might want to send periodic reminders eg 
    # "We noticed that you have not verified yet.  Here is the link again ..."
# So we need a queue over which we have full visibility therefore we must partiton the q by tag groups.

from google.appengine.api import taskqueue as tq
#import umsgpack as mp
import logging
from config import appCfg
#import util
try:  import simplejson as json
except ImportError: import json

LeaseMax = 3 if appCfg.development else 1000
TagMaxMargin = LeaseMax//100 #We want to limit number tasks in any tag group to less than LeaseMax because tasks beyond LeaseMax are invisible .
# But as GAE scales, so several instances/threads might insert a Task by  concurrently by calling MidStore.put() 
# Rather that a Lock we use a safety margin, but remember it might sometimes be exceeded
TagMAX = LeaseMax-TagMaxMargin

N = appCfg.NonceLEN()
def key(token): return token[:N]
def tag(token): return token[N:]      

class VerifyData (object):
    def __init__ (_s, ema=None, uname=None, data=None):
        assert bool(ema)  == bool(uname) , 'must have uname if we have ema and vice versa'
        assert bool(data) != bool(uname) , 'must have uname or data but not both'
        if data:
            _s.data = data
        else:
            assert ' ' not in uname, 'uname has space: "%s"' % uname
            _s.data = uname+' '+ema
        _s.n = -1
        
    def __repr__(_s):        
        return  "<uname: %s, ema: %s>" % (_s.uname(), _s.ema())
                        
#    @property
    def _n (_s):      
        if _s.n == -1:
            _s.n = _s.data.find(' ')
        return _s.n    
         
    def ema (_s): 
        return _s.data[_s._n()+1:]

    def uname(_s):      
        return _s.data[:_s._n()]

        
def hasEma(ema):
    def taskHasEma(task):
        vd = VerifyData(data=task.payload)
        logging.debug('ema = %r', ema)  
        logging.debug('vd = %r', vd)  
        return vd.ema() == ema
    return taskHasEma
    
class Midstore (object):
    
    def __init__(_s, queueName):
        _s.queue = tq.Queue(queueName)
    #    _s.mc = memcache.Client()
    
    def length (_s):
        '''NB the Docs say this: 
        It is not always possible to accurately determine the value for the `tasks` field.
        Use this field with caution.
        '''
        statsList = tq.QueueStatistics.fetch([_s.queue]) 
        return statsList[0].tasks
        
    def _getTasks (_s, token, lease_seconds=0.0):
        return _s.queue.lease_tasks_by_tag( lease_seconds # int or float >= 0.0  Access to task is locked for this worker to complete and possibly delete task. If not, after this time another worker can lease. 
                                          , 1000 # max_tasks:- The maximum number of tasks to lease from the pull queue, up to 1000 tasks.
                                          , tag(token)
                                          )
                                          
#    def _firstTag(_s):
        
    
    def put (_s, nonce, ema, uname): 
        '''caller provides a key which must be unique - not in use for any other task in the Queue'''
    #    _s._deleteTasks(key)
        #find first tag group with space for a new task
        vd = VerifyData(ema, uname)
        tasks, addtag = _s.findAll(hasEma(ema), pop=True, addname=nonce, addpayload=vd.data)
        if tasks:
            for t in tasks:
                logging.debug('Deleted task: %r', t)
        else:   logging.debug('No tasks deleted')
        # assert isinstance(key, str)
        # vdata = VerifyData(ema, uname)

        # n = 0
        # while True:
            # tag = 'tag' + str(n)
            # tasks = _s._getTasks(tag)
            # emaTasks = [t for t if hasEma(t) ]
            # ok = len(tasks) - len(emaTasks) < TagMAX 
            # _s.queue.delete_tasks(emaTasks)
            # if ok: # allow for some (up to max 9?) tasks created concurrently with this instance
                # break
            # n+=1
           
        #d = mp.packb(data)
        #d = json.dumps(data)
        # _s.queue.add (t)
        # logging.debug('added task = %r', t)
        return addtag
  #      _s.mc.set(key, d)

    def _find (_s, tasks, key):
        logging.debug('tasks = %r', tasks)
        n = len(tasks)
        if n == 0:
            logging.warning('No pullq task for tag %s!', tag) # todo try again message ?
            return None
        if n > TagMAX:    
            logging.warning('Extra (%d) pullq tasks for tag %s!', n, tag)
        task = next((t for t in tasks if t.name==key), None) 
        if task:
            assert len([i for i,t in enumerate(tasks) if t.name==key]) == 1, 'one and only one task with key'
            p = task.payload
            logging.debug('payload found: %r' % p)
            return decodeVerifyData(p) # mp.unpackb(p)  
        logging.warning('No task found for key %s!', key)       
            
    def get (_s, token):
        tasks = _s._getTasks(token)
        return _s._find(tasks, key(token))
        
    def pop (_s, token): 
        tasks = _s._getTasks(token, 0.1)
        k = key(token)
        p = _s._find(tasks, k)
        _s.queue.delete_tasks_by_name(k)
        return p
        
    def findAll(_s, pred, pop=False, addname=None, addpayload=None):
        ''' return all tasks fulfilling pred 
            If 'pop' then remove them all from the queue
            If 'addname' is provided then a task is added to the queue, 
                with 'addname' and 'addpayload' and using first tag where there is space
            pred(t) is a function taking Task t and returning bool'''
        rv = {}
        total = _s.length()
        logging.debug('length = %r', total)  
        tn = 0
        nulRunMAX = 3 #todo get from cfg
        nulRuns = 0 # a run of consecutive loops that fail to find a task t returning true for pred(t)
        addtag = None
        while True: 
            tag = 'tag' + str(tn)
            tagTasks = _s._getTasks(tag)
            logging.debug('tag = %r tasks = %r', tag, tagTasks)  
            n = len(tagTasks)
            m = 0
            if n > TagMAX:
                logging.warning('Extra (%d) pullq tagTasks for tag %s!', n, tag)
            if n == 0:
                nulRuns+=1 
                logging.warning('No pullq task for tag %s!', tag) # todo try again message ?
            else:
                nulRuns = 0 
                predTasks = [t for t in tagTasks if pred(t)]
                logging.debug('predTasks = %r', predTasks)
                m = len(predTasks)
                rv[tag] = predTasks
                if pop:
                    for t in predTasks:
                        logging.debug('deleting task: %r', t)
                    _s.queue.delete_tasks(predTasks)
            if addname: 
                if n - m < TagMAX: 
                    addTask2 = tq.Task( payload=addpayload
                                      , name   =addname
                                      , method ='PULL'
                                      , tag    =tag
                                      )
                    _s.queue.add (addTask2)
                    logging.debug('added task = %r', addTask2)
                    addtag = tag
                    addname = None
            total-=n
            if total <= 0 or nulRuns >= nulRunMAX:
                return rv, addtag
            tn+=1
            # todo release all? --  for t in tasks: q.modify_task_lease(t, 0) 
     
    def findEma(_s, loginId):
        if '@' in loginId:
            taskmap, addtag = _s.findAll(hasEma(loginId))
            n = len(taskmap)
            if n:
                if n != 1:
                    logging.warning('multiple tasks (%d) for ema: %s', n, loginId)
                tag, tasks = taskmap.iteritems().next()
                n = len(tasks)
                if n != 1:
                    logging.warning('odd number of tasks (%d) for tag: %s', n, tag)
                t0 = tasks[0]
                logging.debug('found task = %r, %r', tag, t0)
                vd = VerifyData(data=t0.payload)
                return  {'nonce': t0.name
                        ,'ema'  : vd.ema()
                        ,'name' : vd.uname()
                        ,'tag'  : tag
                        }
        return None
        
        
     # def findByEma(_s, ema):
        # def hasEma(t):
            # data = json.loads(t.payload)
            # return data.get('email_') == ema
        # return _s.findAll(hasEma)
            
    # def deleteAllEma(_s, ema):
        # tt = _s.findByEma(ema)
        # for t in tt:
            # logging.debug('deleting task: %r', t)
        # _s.queue.delete_tasks(tt)

    # def delete (_s, key):
        # _s.mc.delete(key)
        # _s._deleteTasks(key)
        
    # def _deleteTasks (_s, key):
        # tasks = _s._getTasks(key)
        # logging.debug('Deleting %d old tasks for %s!', len(tasks), key)
        # if tasks:
            # _s.queue.delete_tasks(tasks)
    

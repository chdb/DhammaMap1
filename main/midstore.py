from google.appengine.api import taskqueue as tq
from google.appengine.api import memcache
import logging
import util as u
import Libs.umsgpack as mp

# GAE's datastore is good for long term storage but can be pricey
# MemCache is free and good for short term/non-reliant use - sometimes items are evicited within minutes by the system
# Data can be saved in PullQueue for up to 30 days but might not be available for the first minute or so.
# So for mid-term storage(up to 30 days max, and mostly reliable) we use the combination of PullQueue and MemCache

# Free Quota: up to 10 named queues + default(unamed) queue
# A Task in a PullQueue can hold: up to   1MB
# A Task in a PushQueue can hold: up to 0.1MB
#  Total data held in all queues: up to 500MB
#  Total tasks in all queues: up to 1 000 000 - but in that case each task would hold on average no more 500 bytes

# The PullQueue TaskQueue API has some limitations
 # The only way to see tasks is to  call lease_tasks() or lease_tasks_by_tag()(or async equivalents)
 # Both these allow you to see max 1000 tasks at each call.  According to an SO answer, lease_tasks()
 # actually always fetchs the tasks in order of eta so perhaps should be really called lease_tasks_by_eta()
 # In any case we can expect the same list of tasks from each repeated call of lease_tasks() - assuming none are deleted eg by another worker
 # In short - you can never use lease_tasks() to see beyond the first 1000 in the PullQueue.

 # However we could use lease_tasks_by_tag() to view all tasks in the queue up to any number of tasks up to 1000 x N-
    # 1) partition the tasks into N groups
        # each group has a unique tag
        # each group has less than 1001 tasks
    # 2) keep a record of the tags
    # 3) loop through all the tags calling  lease_tasks_by_tag(1000)

 # Athough every task has a unique name, there is no lease_tasks_by_name()
 # Instead you can use the tag to hold a unique key or name and you will get your task directly by calling lease_tasks_by_tag().
 # But sometimes this might be a bad design because you will not be able to use the tag to partition the tasks as described above

 # The design trade-off - either use unique tags for direct access to find a task, but forego all queue visibility beyond first 1000
 # - Or use partitoned tags(with extra code) to see the whole queue, but to find a task you will have to search within a tag group


class MidStore(object):

    def __init__(_s):
        _s.queue = tq.Queue('pullq')
        _s.mc = memcache.Client()

    def _getTasks(_s, key):
        return _s.queue.lease_tasks_by_tag( 1 # lease_seconds:- int or float >= 0.0  Access to task is locked for this worker to complete and possibly delete task. If not, after this time another worker can lease.
                                          , 1000 # max_tasks:- The maximum number of tasks to lease from the pull queue, up to 1000 tasks.
                                          , tag=key)

    def put(_s, key, data):
        _s._deleteTasks(key)
        d = mp.packb(data)
        t = tq.Task(method='PULL', payload=d , tag=key)#, eta:= not available to lease() APIs until after eta, then returned by lease() in order of eta(?)
        _s.queue.add(t)
        logging.debug('added task = %r', t)
        _s.mc.set(key, d)

    def get(_s, key):
        p = _s.mc.get(key)
        if not p:
            tasks = _s._getTasks(key)
            logging.debug('tasks = %r', tasks)
            n = len(tasks)
            if n == 0:
                logging.warning('Not one single pullq task for %s!', key) # todo try again message ?
                return None
            if n > 1:
                logging.warning('Multiple(%d) pullq task for %s!', n, key)
            p = tasks[n-1].payload # There should only be one, but anyway choose the last one ...
            logging.debug('payload found: %r' % p)
        return mp.unpackb(p)

    def delete(_s, key):
        _s.mc.delete(key)
        _s._deleteTasks(key)

    def _deleteTasks(_s, key):
        tasks = _s._getTasks(key)
        logging.debug('Deleting %d old tasks for %s!', len(tasks), key)
        if tasks:
            _s.queue.delete_tasks(tasks)

#-------------------------------------------------------------------------------------

def tqSave(tag_, nonce, pname):
    ms = MidStore()
    params={pname:nonce}
    ms.put(tag_, params)


def tqCompare(tag_, token, pname):
    ms = MidStore()
    data = ms.get(tag_)
    if data:
        nonce = data[pname]
        ms.delete(tag_)
        return u.sameStr(token, nonce)
    return False

#------------------------------------

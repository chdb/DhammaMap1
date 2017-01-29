import util
import sys
import secret

def newKey():
    return util.randomB64(), util.sNow()
    
def prettyList(ls):
    '''A python object, EG list, converted to a string by str(), has no formatting.
       Before injecting the string as code into this source file,
       we add spaces and linebreaks to create a pretty list format. 
    '''
    txt = str(ls)
    txt = txt.replace('['  , '[ '           )
    txt = txt.replace('),' , ')\n        ,' )    
    txt = txt.replace(']'  ,  '\n        ]' )
    return txt
    
def update (addNew, purge):
    assert addNew or purge
    n = 0 # number of purged keys
    with open('secret.py', 'r+') as f:
        txt = f.read()
        p = txt.find('keys =  [')
        assert p > 0, "cant find variable: 'keys'"
        q = txt.find(']', p) + 1
        if purge:  # remove outdated keys
            maxAge = ??? # seconds  # todo !!! 
            t = util.sNow() - maxAge
            n = len(secret.keys)
            secret.keys = [i for i in secret.keys if i[1] >= t] 
            n -= len(secret.keys)
        if addNew:   
            secret.keys.append(newKey())          
        f.seek(0)           # go back to start ( read() has moved us to end )
        f.write ( txt[:p]    
                +'keys =  ' + prettyList(secret.keys)
                + txt[q:]
                )           # overwrite
        f.truncate()        # set eof, in case its shorter than before
    return n

def run():
    nArgs = len(sys.argv)
    if nArgs == 2:
        a = sys.argv[1]
        if a == '-addNew':
            update (True, False)
            return True,'new key added'     
        if a == '-purge':
            n = update (False, True)
            return True,'%d outdated keys purged' % n    
        if a == '-both':
            n = update (True, True)
            return True,'new key added and %d outdated keys purged' % n 
        return False,'invalid option argument'
    if nArgs == 1:
        return False,'missing an argument'
    return False,'too many arguments'

       
if __name__ == '__main__':
    ok,result = run()
    if ok:
        print 'success: ' + result
    else:
        print 'error: ' + result
        print 'syntax:  python update.py -addNew    # adds a new key'
        print '         python update.py -purge     # purges outdated keys'
        print '         python update.py -both      # both adds and purges '

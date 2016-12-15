import util
import sys
import secret

def newKey():
    return util.randomB64(), util.sNow()
    
def prettyList(ls):
    '''A python object, EG list, converted to a string by str(), has no formatting.
       Before injecting the string as code into this source file,
       we add spaces and linebreaks to create the list format as used above for 'keys'. 
    '''
    txt = str(ls)
    txt = txt.replace('['  , '[ '           )
    txt = txt.replace('),' , ')\n        ,' )    
    txt = txt.replace(']'  ,  '\n        ]' )
    return txt
    
def update (addNew, purge):
    assert addNew or purge
    n = 0 #number of purged key
     
    with open('secret.py', 'r+') as f:
        txt = f.read()
        p = txt.find('keys =  [')
        assert p > 0, "cant find variable: 'keys'"
        q = txt.find(']', p) + 1
        
        
        if purge:  # remove outdated keys
            maxAge = 2000 # todo !!! 
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
                )           # overwrites
        f.truncate()        # eof in case its shorter than before
        return n

def run():
    nArgs = len(sys.argv)
    if nArgs == 2:
        a = sys.argv[1]
        if a == '-addNew':
            update (True, False)
            print 'success: new key added'     
        elif a == '-purge':
            n = update (False, True)
            print 'success: %d outdated keys purged' % n    
        elif a == '-both':
            n = update (True, True)
            print 'success: new key added and %d outdated keys purged' % n 
        else:
            return 'invalid argument'
        return 'ok'
    if nArgs == 1:
        return 'missing one argument'
    return 'too many arguments'

       
if __name__ == '__main__':
    result = run()
    if result != 'ok':
        print result
        print 'syntax:  python update.py -addNew    # adds a new key'
        print '         python update.py -purge     # purges outdated keys'
        print '         python update.py -both      # both adds and purges '

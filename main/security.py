import env
import logging
from passlib.context import CryptContext

defRounds_sha512 =(10000 if env.ENV['development'] else
                    80000)
logging.info('@@@@@@@ default rounds sha512 = %d @@@@@@@@', defRounds_sha512)

pwd = CryptContext( schemes = ['sha512_crypt'
                              ,'pbkdf2_sha512'
                              ,'bcrypt'
                              ]
                  , sha512_crypt__default_rounds = defRounds_sha512
               #  , deprecated =['bcrypt' # now stored hash can be replaced using eg verify_and_update()
               #                ]
               #  , bcrypt__min_rounds = 4000
               #  , bcrypt__max_rounds = 5000
                  )


# move bcrypt to 1st choice
# myctx.update(default="bcrypt")

#instead of samestr use this:-
#       from passlib.utils import consteq
# def sameStr(a, b):
    # def _sameStr(a, b): # a version of this is in python 3 and 2.7.7 as hmac.compare_digest
        # """Checks if two strings, a, b have identical content.
        # The running time of this algorithm is more or less independent of the length of the common substring.
        # The standard implementation ie a == b is subject to timing attacks, because the execution time is
        # roughly proportional to the length of the common substring.
        # """
        #logging.debug('a: %s', a)
        #logging.debug('b: %s', b)
        # if len(a) != len(b):
            # return False
        # r = 0
        # for x, y in zip(a, b):
            # r |= ord(x) ^ ord(y)
            # # logging.debug('r: %s', r)
        # return r == 0

    # r = _sameStr(a, b)
    # if not r:
        # logging.debug('different XXXXXXXXXXXXXXXXXXXXXXXXX a: %r ', a)
        # logging.debug('different XXXXXXXXXXXXXXXXXXXXXXXXX b: %r ', b)
    # return r

import config
import logging
from passlib.context import CryptContext

defRounds_sha512 = 10000 if config.DEVELOPMENT else 80000
logging.info('@@@@@@@ default rounds sha512 = %d @@@@@@@@', defRounds_sha512)

pwd = CryptContext( schemes = ['sha512_crypt'
                              ,'pbkdf2_sha512'
                              ,'bcrypt'
                              ]
                  , sha512_crypt__default_rounds = defRounds_sha512
               #  ,deprecated =['bcrypt' # now stored hash can be replaced using eg verify_and_update() 
               #                ]
               #  ,bcrypt__min_rounds = 4000            
               #  ,bcrypt__max_rounds = 5000            
                  )


# move bcrypt to 1st choice
# myctx.update(default="bcrypt")

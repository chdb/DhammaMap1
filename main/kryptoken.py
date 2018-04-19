#!/usr/bin/python
# -*- coding: utf-8 -*-
#from __future__ import unicode_literals

import hashlib
import hmac
import os
import json
import util as u
import widget as W
from passlib.utils import consteq
import logging

from base64 import urlsafe_b64encode\
                 , urlsafe_b64decode

class Base64Error(Exception):
    '''invalid Base64 character or incorrect padding'''

def decodeToken(token, expected):
    try:
        td = _decode(token)
        if td.valid(expected):
            if expected == 'session':
                td.data['_created'] = td.timeStamp # dict
            else:
                td.data +=(td.timeStamp,) # tuple
        return td.data

    except Base64Error:
        logging.warning('invalid Base64 in %s Token: %r', expected, token)
    except:
        logging.exception('unexpected exception decoding %s token : %r', expected, token)
    return None, False

def encodeVerifyToken(data, tt):
   # tt = _tokenType(tt)
    assert tt in ['signUp'
                 ,'pw1'
                 ,'pw2'
                 ], 'invalid TokenType: %s' % tt
    return _encode(tt, data)

def encodeSessionToken(ssn):#, user=None):
    data = dict(ssn)

    if '_userID' in ssn:
        return _encode('auth', data)
    return _encode('anon', data)

TokenTypes =( 'anon'
             , 'auth'
             , 'signUp'
             , 'pw1'
             )
def _tokenTypeCode(tt): return TokenTypes.index(tt)
def _tokenType(code):   return TokenTypes [code]
#.........................................

class _TokenData(object):

    def __init__(_s, token, tt, obj, bM, ts):
        _s.badMac  = bM
        _s.tokenType = tt
        _s.timeStamp = ts
        _s.token = token
        _s.data  = obj

    def valid(_s, expected):
        """ Checks encryption validity
        Use neutral evaluation pathways to beat timing attacks.
        NB: return only success or failure - log shows why it failed but user mustn't know !
        """
        if expected == 'session':
            badType =(_s.tokenType != 'anon'
                   and _s.tokenType != 'auth')
        else:
            badType =  _s.tokenType != expected
        badData = _s.data is None #  and(type(_s.data) == dict)
        bad = None
        # check booleans in order of their initialisation
        if _s.badMac: bad ='Invalid MAC'
        elif badType: bad ='Invalid token ttype:{} expected:{}'.format(_s.tokenType, expected)
        elif badData: bad ='Invalid data object'
        if bad:
            logging.warning('%s in Token: %r', bad, _s.token)
        return not bad
 #.........................................
# Some global constants to hold the lengths of component substrings of the token
CH  = 1
TS  = 4
UID = 8
MAC = 20
MinTokenLen =(MAC + UID + CH + TS)*4/3

def _hash(msg, ts):
    """hmac output of sha1 is 20 bytes irrespective of msg length"""
    k = W.W.keys(ts)
    return hmac.new(k, msg, hashlib.sha1).digest()

def _serialize(data):
    '''Generic data is stored in the token. The data could be a dict or any other serialisable type.
    However the data size is limited because currently it all goes into one cookie and
    there is a max cookie size for some browsers so we place a limit in session.save()
    '''
    # ToDo: replace json with binary protocol cpickle
    # ToDo compression of data thats too long to fit otherwise:
    # data = json.encode(data)
    # if len(data) > data_max: # 4K minus the other fields
        # level =(len(data) - data_max) * K  # experiment! or use level = 9
        # data = zlib.compress( data, level)
        # if len(data) > data_max:
            # assert False, 'oh dear!' todo - save some? data in datastore
        # return data, True
    # return data, False    # todo: encode a boolean in kch to indicate whether compressed
    #logging.debug('serializing data = %r', data)
    s = json.dumps(data, separators=(',',':'))
    #logging.debug('serialized data: %r', s)
    return s.encode('utf-8') #byte str

def _deserialize(data):
    try:
        # logging.debug('data1: %r', data)
        obj = json.loads(data)
        # logging.debug('obj: %r', obj)
        return obj # byteify(obj)
    except Exception, e:
        logging.exception(e)
        return None

def _encode(tokentype, obj):
    """ obj is serializable session data
        returns a token string of base64 chars with iv and encrypted tokentype and data
    """
    tt = _tokenTypeCode(tokentype)
    logging.debug('encode tokentype = %r tt = %r',tokentype, tt)
    now = u.sNow()
    #logging.debug('encode tokentype = %r tt = %r',tokentype, tt)
    data = W._iB.pack(now, tt)             # ts + tt
    data += _serialize(obj)               # ts + tt + data
    h20 = _hash(data, now)
    return urlsafe_b64encode(data + h20)   # ts + tt + data + mac

def _decode(token):
    """inverse of encode: return _TokenData"""
    try:
        bytes = urlsafe_b64decode(token)   # ts + tt + data + mac
    except TypeError:
        logging.warning('Base64 Error: token = %r', token)
        logging.exception('Base64 Error: ')
        raise Base64Error

    ts, tt = W._iB.unpack_from(bytes)
    ttype = _tokenType(tt)
    # logging.debug('decode tokentype = %r tt = %r token = %s',ttype, tt, token)
    preDataLen = TS+CH
    data = bytes[ :-MAC]
    mac1 = bytes[-MAC: ]
    mac2 = _hash(data, ts)
    badMac = not consteq(mac1, mac2)
    data = _deserialize(data [preDataLen: ])
    # logging.debug('data: %r', data)
    return _TokenData(token, ttype, data, badMac, ts)

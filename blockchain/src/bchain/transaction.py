from enum import Enum
from datetime import datetime
from ellipticcurve import PrivateKey, PublicKey, Ecdsa, Signature
from pickle import dumps, loads
import type_enforced
import base64

class TTypes(Enum):
    transfer = 1
    publishContract = 2
    executeContract = 3

@type_enforced.Enforcer
class Address():
    __slots__ = ['address']
    def __init__(self, address: str = "", pkey : [None, PublicKey] = None, pkey_compressed : str = "") -> None:
        if(not(pkey is None)):
            self.address = "0x" + pkey.toCompressed()[-40:]
        elif(pkey_compressed):
            if(len(pkey_compressed) < 40):
                raise ValueError("Public key is too short to create address")
            self.address = "0x" + pkey_compressed[-40:]
        else:
            self.address = address
        if(not self.validate(self.address)):
            raise ValueError("Address must be a hexadecimal string with length of 42")

    def __call__(self) -> str:
        return self.address

    def getAddr(self) -> str:
        return self.address
    
    @staticmethod
    def validate(address: str) -> bool:
        ret = True
        ret = ret and (len(address) == 42)
        ret = ret and address.startswith('0x')
        return ret

@type_enforced.Enforcer
class Transaction():
    __slots__ = ['data', '_datastring', '_signature']

    def __init__(self, ttype : TTypes, fromAddr : Address, toAddr : Address, pkey : [str, PublicKey], value : int, fee : int, ckey : [None, PrivateKey] = None,  msg : [None, object] = None, datastring : [None, str] = None, timestamp : [None, datetime] = None, signature : [None, str] = None) -> None:
        self.data = dict.fromkeys(['ttype', 'timestamp', 'fromAddr', 'toAddr', 'pkey', 'value', 'fee', 'msg'])
        self.data['ttype'] = ttype
        self.data['timestamp'] = timestamp or datetime.now()
        self.data['fromAddr'] = fromAddr
        self.data['toAddr'] = toAddr
        if(isinstance(pkey, PublicKey)):
            self.data['pkey'] = pkey.toCompressed()
        else:
            self.data['pkey'] = pkey
        self.data['value'] = value
        self.data['fee'] = fee
        self.data['msg'] = msg
        
        self._datastring = self.encodeDatastring(self.data)
        if(datastring and datastring != self._datastring):
            raise Exception("Datastrings from created and imported transactions don't match")
        self._signature = signature or Ecdsa.sign(self._datastring, ckey).toBase64()
        if(not self.validate(self._datastring, self._signature)):
                raise ValueError("Validation of a transaction has failed")
    
    @property
    def datastring(self) -> str:
        return self._datastring

    @property
    def signature(self) -> str:
        return self._signature
    
    @classmethod
    def fromDatastring(cls, datastring : str, signature : str):
        data = cls.decodeDatastring(datastring)
        return cls(**data, datastring = datastring, signature = signature)
    
    @classmethod
    def validate(cls, datastring : str, signature : str) -> bool:
        ret = True
        data = cls.decodeDatastring(datastring)
        if(not Ecdsa.verify(datastring, Signature.fromBase64(signature), PublicKey.fromCompressed(data['pkey']))):
            ret = False
            raise ValueError("Transaction didn't pass signature validation")
        if(not (data["fromAddr"].getAddr()[-40:] == data['pkey'][-40:])):
            ret = False
            raise ValueError("Transaction sender don't own public key")
        return ret

    @staticmethod
    def encodeDatastring(data : dict) -> str:
        ret = dumps(data)
        ret = base64.b64encode(ret).decode('ascii')
        return ret

    @staticmethod
    def decodeDatastring(datastring : str) -> dict:
        ret = base64.b64decode(datastring)
        ret = loads(ret)
        return ret


from enum import Enum
from datetime import datetime
from ellipticcurve import PrivateKey, PublicKey, Ecdsa, Signature
from pickle import dumps, loads
import type_enforced

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
    
    @staticmethod
    def validate(address: str) -> bool:
        ret = True
        ret = ret and (len(address) == 42)
        ret = ret and address.startswith('0x')
        return ret

@type_enforced.Enforcer
class Transaction():
    __slots__ = ['data', 'dataString', 'signature']

    def __init__(self, ttype : TTypes, fromAddr : Address, toAddr : Address, pkey : PublicKey, ckey : PrivateKey, value : int, fee : int, msg : [None, object] = None) -> None:
        data = dict.fromkeys(['ttype', 'timestamp', 'fromAddr', 'toAddr', 'pkey', 'value', 'fee', 'msg'])
        self.data['ttype'] = ttype
        self.data['timestamp'] = datetime.now()
        self.data['fromAddr'] = fromAddr
        self.data['toAddr'] = toAddr
        self.data['pkey'] = pkey.toCompressed()
        self.data['value'] = value
        self.data['fee'] = fee
        self.data['msg'] = msg
        
        self.datastring = dumps(self.data)
        self.signature = Ecdsa.sign(self.datastring, ckey).toDer()
        if(not self.validate(self.dataString, self.signature)):
                raise ValueError("Validation of a transaction has failed")

    def __init__(self, dataString : str, signature : str) -> None:
        self.dataString = dataString
        self.signature = signature
        if(not self.validate(self.dataString, Signature.fromDer(self.signature))):
                raise ValueError("Validation of a transaction has failed")
        data = dict.fromkeys(['ttype', 'timestamp', 'fromAddr', 'toAddr', 'pk', 'value', 'fee', 'msg'])
        self.data = loads(self.dataString)
    
    @staticmethod
    def validate(dataString : str, signature : str) -> bool:
        ret = True
        data = loads(dataString)
        if(not Ecdsa.verify(dataString, signature, PublicKey.fromCompressed(data['pkey']))):
            ret = False
            raise ValueError("Transaction didn't pass signature validation")
        if(not (data.fromAddr[-40:] == data['pkey'][-40:])):
            ret = False
            raise ValueError("Transaction sender don't own public key")
        return ret


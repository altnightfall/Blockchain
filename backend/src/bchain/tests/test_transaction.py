import pytest
from ellipticcurve import PrivateKey, PublicKey
from backend.src.bchain.transaction import Address, Transaction, TTypes

class TestAddress():
    def test_badAddress(self):
        with pytest.raises(Exception):
            Address("FakeAddress")

        with pytest.raises(Exception):
            Address("0x111abc111")

        with pytest.raises(Exception):
            Address("111111111111111111111111111111111111111111")
        
        Address("0x1111111111111111111111111111111111111111")

    def test_badKey(self):
        _ckey = PrivateKey()
        _pkey = _ckey.publicKey()
        _pkey_compressed = _pkey.toCompressed()

        with pytest.raises(Exception):
            Address(pkey_compressed = "FakeKey")

        Address(pkey = _pkey)
        Address(pkey_compressed = _pkey_compressed)

class TestTransaction():
    ckeyFrom = PrivateKey()
    pkeyFrom = ckeyFrom.publicKey()
    ckeyTo = PrivateKey()
    pkeyTo = ckeyTo.publicKey()
    addrFrom = Address(pkey = pkeyFrom)
    addrTo = Address(pkey = pkeyTo)

    def test_badKeyArguments(self):    
        with pytest.raises(Exception):
            Transaction(TTypes.transfer, self.addrFrom, self.addrTo, self.pkeyTo, 100, 1, self.ckeyTo)

        with pytest.raises(Exception):
            Transaction(TTypes.transfer, self.addrFrom, self.addrTo, self.pkeyFrom, 100, 1, self.ckeyTo)

        with pytest.raises(Exception):
            Transaction(TTypes.transfer, self.addrFrom, self.addrTo, self.pkeyTo, 100, 1, self.ckeyFrom)

        Transaction(TTypes.transfer, self.addrFrom, self.addrTo, self.pkeyFrom, 100, 1, self.ckeyFrom)

    def test_badImports(self):
        t1 = Transaction(TTypes.transfer, self.addrFrom, self.addrTo, self.pkeyFrom, 100, 1, self.ckeyFrom)
        datastring1 = t1.datastring
        signature1 = t1.signature
        t2 = Transaction(TTypes.transfer, self.addrFrom, self.addrTo, self.pkeyFrom, 1000, 1, self.ckeyFrom)
        datastring2 = t2.datastring
        signature2 = t2.signature
        with pytest.raises(Exception):
            Transaction.fromDatastring("abd", "adc")

        with pytest.raises(Exception):
            Transaction.fromDatastring("aer", signature1)

        with pytest.raises(Exception):
            Transaction.fromDatastring(datastring1, "dfs")

        with pytest.raises(Exception):
            Transaction.fromDatastring(signature1, datastring1)

        with pytest.raises(Exception):
            Transaction.fromDatastring(datastring2, signature1)
        
        Transaction.fromDatastring(datastring1, signature1)
        Transaction.fromDatastring(datastring2, signature2)

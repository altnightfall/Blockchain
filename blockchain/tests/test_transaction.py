import pytest
from ellipticcurve import PrivateKey, PublicKey
from blockchain.src.bchain.transaction import Address

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

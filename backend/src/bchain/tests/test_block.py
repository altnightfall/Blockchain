import pytest
from backend.src.bchain.constants import Constants
from backend.src.bchain.block import Block, TransactionList
from backend.src.bchain.transaction import TTypes, Transaction, Address
from ellipticcurve import PrivateKey, PublicKey

class TestConstants:
    def test_constants(self):
        assert Constants.BlockSize() == 1
        assert Constants.Difficulty() == 3
        
class TestTransactionList:
    ckeyFrom = PrivateKey()
    pkeyFrom = ckeyFrom.publicKey()
    ckeyTo = PrivateKey()
    pkeyTo = ckeyTo.publicKey()
    addrFrom = Address(pkey = pkeyFrom)
    addrTo = Address(pkey = pkeyTo)
    
    ckeyMiner = PrivateKey()
    pkeyMiner = ckeyMiner.publicKey()
    
    tr = Transaction(TTypes.transfer, addrFrom, addrTo, pkeyFrom, 100, 1, ckeyFrom)
    
    def test_listCreation(self):
        with pytest.raises(Exception):
            TransactionList.validate(TransactionList.create(self.ckeyMiner, None, self.tr, self.tr))
        
        tl = TransactionList.create(self.ckeyMiner, None, self.tr)
        assert tl.data[0].data['ttype'] == TTypes.creationReward
        assert tl.data[0].data['toAddr'].getAddr() == Address(pkey = self.pkeyMiner).getAddr()
        assert tl.data[0].data['value'] == Constants.CreationReward()
        assert tl.data[2].data['ttype'] == TTypes.fee
        assert tl.data[2].data['toAddr'].getAddr() == Address(pkey = self.pkeyMiner).getAddr()
        assert tl.data[2].data['value'] == self.tr.data['fee']
        assert TransactionList.validate(tl)
        
class TestBlock:
    ckeyFrom = PrivateKey()
    pkeyFrom = ckeyFrom.publicKey()
    ckeyTo = PrivateKey()
    pkeyTo = ckeyTo.publicKey()
    addrFrom = Address(pkey = pkeyFrom)
    addrTo = Address(pkey = pkeyTo)
    
    ckeyMiner = PrivateKey()
    pkeyMiner = ckeyMiner.publicKey()
    
    initBlock = Block.createInit(ckeyMiner)
    
    tr = Transaction(TTypes.transfer, addrFrom, addrTo, pkeyFrom, 100, 1, ckeyFrom)
    
    def test_InitBlock(self):
        assert self.initBlock.data['id'] == 0
        assert self.initBlock.getTransaction(0).data['ttype'] == TTypes.creationReward
        assert Block.validate(self.initBlock)
    
    def test_CreateBlock(self):
        block = Block.construct(1, self.initBlock.hash, self.ckeyMiner, self.tr)
        
        assert block.getTransactionListLen() == Constants.BlockSize() + 2
        assert block.getTransaction(0).data['toAddr'].getAddr() == Address(pkey = self.pkeyMiner).getAddr()
        assert block.getTransaction(2).data['toAddr'].getAddr() == Address(pkey = self.pkeyMiner).getAddr()
        assert Block.validate(block)
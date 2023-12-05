from backend.src.bchain.constants import Constants
import hashlib
from backend.src.bchain.transaction import Transaction, TTypes, Address
from pickle import dumps, loads
import type_enforced
import base64
from ellipticcurve import PrivateKey, PublicKey


@type_enforced.Enforcer
class TransactionList:
    __slots__ = ["data"]

    def __init__(self, *transactions: Transaction) -> None:
        self.data = []
        for tr in transactions:
            self.data += [Transaction.fromDatastring(tr.datastring, tr.signature)]

    @staticmethod
    def validate(transactionList) -> bool:
        ret = True
        if transactionList.getLen() != (Constants.BlockSize() + 2):
            ret = False
            raise ValueError("Length of a transaction section is not right")
        sfee = 0
        for tr in transactionList.data:
            if not (isinstance(tr, Transaction)):
                ret = False
                raise ValueError("Not a transaction in a list")
            sfee += tr.data["fee"]
        if transactionList.data[0].data["ttype"] != TTypes.creationReward:
            ret = False
            raise ValueError("First transaction is not a block creation reward")
        if transactionList.data[-1].data["ttype"] != TTypes.fee:
            ret = False
            raise ValueError("Last transaction is not a fee reward")
        if transactionList.data[0].data["value"] != Constants.CreationReward():
            ret = False
            raise ValueError("Creation reward is not right")
        if transactionList.data[-1].data["value"] != sfee:
            ret = False
            raise ValueError("Fee reward is not right")
        return ret

    @classmethod
    def create(
        cls,
        ckey: PrivateKey,
        address: [None, Address] = None,
        *transactions: Transaction
    ):
        pkey = ckey.publicKey()
        addr = Address(address, pkey if address is None else None)
        trcreation = Transaction(
            TTypes.creationReward, None, addr, pkey, Constants.CreationReward(), 0, ckey
        )
        trlist = list(transactions)
        sfee = 0
        for tr in trlist:
            sfee += tr.data["fee"]
        trfee = Transaction(TTypes.fee, None, addr, pkey, sfee, 0, ckey)
        trlist = [trcreation] + trlist + [trfee]
        return cls(*trlist)

    def getTransaction(self, num: int) -> Transaction:
        return self.data[num]

    def getLen(self) -> int:
        return len(self.data)


@type_enforced.Enforcer
class Block:
    __slots__ = ["data", "_datastring", "_hash"]

    def __init__(
        self,
        id: int,
        prevHash: str,
        transactionList: TransactionList,
        nonce: int = 0,
        datastring: [None, str] = None,
        hash: [None, str] = None,
    ) -> None:
        self.data = dict.fromkeys(["id", "prevHash", "transactionList", "nonce"])
        self.data["id"] = id
        self.data["prevHash"] = prevHash
        self.data["transactionList"] = transactionList
        self.data["nonce"] = nonce

        self._datastring = self.encodeDatastring(self.data)
        if datastring and self._datastring != datastring:
            raise ValueError("Datastrings from created and imported blocks don't match")
        self._hash = hashlib.sha256(self._datastring.encode("utf-8")).hexdigest()
        if hash and self._hash != hash:
            raise ValueError("Hashes from created and imported blocks don't match")

    @property
    def datastring(self) -> str:
        return self._datastring

    @property
    def hash(self) -> str:
        return self._hash

    def isMined(self) -> bool:
        return self.hash[: Constants.Difficulty()] == "0" * Constants.Difficulty()

    def mine(self) -> None:
        while not self.isMined():
            self.data["nonce"] += 1
            self._datastring = self.encodeDatastring(self.data)
            self._hash = hashlib.sha256(self.datastring.encode("utf-8")).hexdigest()

    def validate(self) -> bool:
        ret = True
        datastring = self.encodeDatastring(self.data)
        if not isinstance(self, Block):
            ret = False
            raise ValueError("Is not a block")
        if self.datastring != datastring:
            ret = False
            raise ValueError("Datastring is not right")
        hash = hashlib.sha256(self.datastring.encode("utf-8")).hexdigest()
        if self.hash != hash:
            ret = False
            raise ValueError("Hash is not right")

        if self.data["id"] == 0:
            ret = True
            return ret

        if not isinstance(self.data["transactionList"], TransactionList) and not (
            self.data["transactionList"].validate()
        ):
            ret = False
            raise ValueError("Transaction list isn't right")
        if not self.isMined():
            ret = False
            raise ValueError("Block hasn't been mined")
        return ret

    @classmethod
    def fromDatastring(cls, datastring: str, hash: str):
        data = cls.decodeDatastring(datastring)
        return cls(**data, datastring=datastring, hash=hash)

    @staticmethod
    def encodeDatastring(data: dict) -> str:
        ret = dumps(data)
        ret = base64.b64encode(ret).decode("ascii")
        return ret

    @staticmethod
    def decodeDatastring(datastring: str) -> dict:
        ret = base64.b64decode(datastring)
        ret = loads(ret)
        return ret

    @classmethod
    def createInit(cls, ckey: PrivateKey):
        pkey = ckey.publicKey()
        addr = Address(pkey=pkey)
        initTransaction = Transaction(
            TTypes.creationReward, None, addr, pkey, Constants.CreationReward(), 0, ckey
        )
        return cls(0, "FunnyMonke", TransactionList(initTransaction))

    @classmethod
    def construct(
        cls, id: int, prevHash: str, ckey: PrivateKey, *transactions: Transaction
    ):
        trlist = TransactionList.create(ckey, None, *transactions)
        block = cls(id, prevHash, trlist)
        block.mine()
        ret = block.validate()
        if ret:
            return block
        else:
            raise ValueError("Block can't be validated")

    def getTransaction(self, num: int) -> Transaction:
        return self.data["transactionList"].getTransaction(num)

    def getTransactionListLen(self) -> int:
        return self.data["transactionList"].getLen()

    def to_dict(self) -> dict:
        pass

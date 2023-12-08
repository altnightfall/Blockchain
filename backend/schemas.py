from pydantic import BaseModel
from datetime import datetime


class AddressBase(BaseModel):
    address: str


class AddressCreate(AddressBase):
    pass


class Address(AddressBase):
    id: int


class AddressBalance(BaseModel):
    address: Address
    balance: float


class TransactionBase(BaseModel):
    ttype: int
    ttimestamp: datetime
    fromAddr: Address | None = None
    toAddr: Address | None = None
    value: float
    fee: float
    data: str
    msg: str | None = None


class TransactionCreate(TransactionBase):
    fromAddr: Address | None = None
    toAddr: Address | None = None
    msg: str | None = None


class TransactionUpdate(TransactionBase):
    pass


class TransactionUpdatePartial(TransactionBase):
    ttype: int | None = None
    ttimestamp: datetime | None = None
    fromAddr: Address | None = None
    toAddr: Address | None = None
    value: float | None = None
    fee: float | None = None
    data: str | None = None
    msg: str | None = None


class Transaction(TransactionBase):
    id: int


class BlockBase(BaseModel):
    prevHash: str
    transactionList: list[int]
    nonce: int
    datastring: str
    hash: str


class BlockCreate(BlockBase):
    pass


class BlockUpdate(BlockCreate):
    pass


class BlockUpdatePartial(BlockCreate):
    prevHash: str | None = None
    transactionList: list[Transaction] | None = None
    nonce: int | None = None
    datastring: str | None = None
    hash: str | None = None


class Block(BlockBase):
    id: int
    transactionList: list[Transaction]

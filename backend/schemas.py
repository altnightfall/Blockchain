from pydantic import BaseModel
from datetime import datetime


class AddressBase(BaseModel):
    address: str


class AddressCreate(AddressBase):
    pass


class Address(AddressBase):
    id: int


class TransactionBase(BaseModel):
    ttype: int
    ttimestamp: datetime
    fromAddr: int
    toAddr: int
    value: int
    fee: int
    data: int
    msg: str


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(TransactionBase):
    pass


class TransactionUpdatePartial(TransactionBase):
    ttype: int | None = None
    ttimestamp: datetime | None = None
    fromAddr: Address | None = None
    toAddr: Address | None = None
    value: int | None = None
    data: int | None = None
    msg: str | None = None


class Transaction(TransactionBase):
    id: int


class BlockBase(BaseModel):
    prevHash: str
    transactionList: list[Transaction]
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

from pydantic import BaseModel
from datetime import datetime


class AddressBase(BaseModel):
    address: str


class AddressCreate(AddressBase):
    ckey: str


class Address(AddressBase):
    id: int


class AddressBalance(BaseModel):
    address: Address
    balance: float


class TransactionBase(BaseModel):
    ttype: int
    fromAddr: int | None = None
    toAddr: int | None = None
    value: int
    fee: int
    ttimestamp: datetime


class TransactionCreate(TransactionBase):
    fromAddr: int | None = None
    toAddr: int | None = None
    pkey: str
    data: str
    signature: str


class TransactionUpdate(TransactionBase):
    pass


class TransactionUpdatePartial(TransactionBase):
    ttype: int | None = None
    ttimestamp: datetime | None = None
    fromAddr: Address | None = None
    toAddr: Address | None = None
    value: int | None = None
    fee: int | None = None


class Transaction(TransactionBase):
    fromAddr: Address | None
    toAddr: Address | None
    id: int
    data: str
    signature: str
    block_id: int | None


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

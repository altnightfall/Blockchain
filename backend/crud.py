from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Block, Transaction, Address
from schemas import (
    AddressCreate,
    BlockCreate,
    BlockUpdate,
    TransactionCreate,
    TransactionUpdate,
    BlockUpdatePartial,
    TransactionUpdatePartial,
)


async def create_address(session: AsyncSession, address_inp: AddressCreate) -> Address:
    address = Address(**address_inp.model_dump())
    session.add(address)
    await session.commit()
    return address


async def create_transaction(
    session: AsyncSession, transaction_inp: TransactionCreate
) -> Transaction:
    for address in [transaction_inp.fromAddr, transaction_inp.toAddr]:
        if not await get_address_by_id(session=session, address_id=address):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Address with ID {address} does not exist",
            )
    transaction = Transaction(**transaction_inp.model_dump())
    session.add(transaction)
    await session.commit()
    return transaction


async def create_block(session: AsyncSession, block_inp: BlockCreate) -> Block:
    for transaction in block_inp.transactionList:
        await create_transaction(session, TransactionCreate(**transaction.model_dump()))
    block = Block(**block_inp.model_dump())
    session.add(block)
    await session.commit()

    return block


async def get_blocks(session: AsyncSession) -> list[Block]:
    stmt = select(Block).order_by(Block.id)
    result: Result = await session.execute(stmt)
    blocks = result.scalars().all()
    return list(blocks)


async def get_address(session: AsyncSession, address: str) -> Address | None:
    stmt = select(Address).where(Address.address == address)
    return await session.scalar(stmt)


async def get_address_by_id(session: AsyncSession, address_id: int) -> Address | None:
    return await session.get(Address, address_id)


async def get_minimum_fee(session: AsyncSession) -> float:
    stmt = select(Transaction).order_by(Transaction.fee).limit(1)
    return (await session.scalar(stmt)).fee


async def get_transaction_by_fee(
    session: AsyncSession, fee: float = None
) -> list[Transaction]:
    if fee is None:
        fee = await get_minimum_fee(session)
    stmt = select(Transaction).where(Transaction.fee >= fee)
    return list(await session.scalars(stmt))


async def get_block_by_id(session: AsyncSession, block_id: int) -> Block | None:
    return await session.get(Block, block_id)


async def update_transaction(
    session: AsyncSession,
    transaction: Transaction,
    transaction_update: TransactionUpdate | TransactionUpdatePartial,
    partial: bool = False,
) -> Transaction:
    for name, value in transaction_update.model_dump(exclude_unset=partial).items():
        setattr(transaction, name, value)
    await session.commit()
    return transaction


async def update_block(
    session: AsyncSession,
    block: Block,
    block_update: BlockUpdate | BlockUpdatePartial,
    partial: bool = False,
) -> Block:
    for name, value in block_update.model_dump(exclude_unset=partial).items():
        setattr(block, name, value)
    await session.commit()
    return block


async def delete_block_by_id(session: AsyncSession, block: Block) -> None:
    await session.delete(block)
    await session.commit()

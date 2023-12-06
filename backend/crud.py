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
        if not await get_address(session=session, address=address.address):
            await create_address(
                session=session, address_inp=AddressCreate(**address.model_dump())
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

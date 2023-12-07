from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.bchain.transaction import (
    Transaction as TransactionClass,
    Address as AddressClass,
)

from backend.core.models import (
    Block,
    Transaction as TransactionModel,
    Address as AddressModel,
)
from backend.schemas import (
    AddressCreate,
    BlockCreate,
    BlockUpdate,
    TransactionCreate,
    TransactionUpdate,
    BlockUpdatePartial,
    TransactionUpdatePartial,
)


async def create_address(
    session: AsyncSession, address_inp: AddressCreate
) -> AddressModel:
    if not AddressClass.validate(address_inp.address):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not validate address {address_inp.address}",
        )

    if await get_address(session, address_inp.address) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Address {address_inp.address} already exists",
        )

    address = AddressModel(**address_inp.model_dump())
    session.add(address)
    await session.commit()
    return address


async def create_transaction(
    session: AsyncSession, transaction_inp: TransactionCreate
) -> TransactionModel:
    for address in [transaction_inp.fromAddr, transaction_inp.toAddr]:
        if not await get_address_by_id(session=session, address_id=address):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Address with ID {address} does not exist",
            )
    transaction = TransactionModel(**transaction_inp.model_dump())
    session.add(transaction)
    await session.commit()
    return transaction


async def create_block(session: AsyncSession, block_inp: BlockCreate) -> Block:
    for transaction in block_inp.transactionList:
        if (
            await get_transaction_by_id(session=session, transaction_id=transaction)
            is None
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transaction {transaction} not found!",
            )
    block = Block(**block_inp.model_dump())
    session.add(block)
    await session.commit()

    return block


async def get_address(session: AsyncSession, address: str) -> AddressModel | None:
    stmt = select(AddressModel).where(AddressModel.address == address)
    return await session.scalar(stmt)


async def get_address_by_id(
    session: AsyncSession, address_id: int
) -> AddressModel | None:
    return await session.get(AddressModel, address_id)


async def get_transaction_by_id(
    session: AsyncSession, transaction_id: int
) -> TransactionModel | None:
    return await session.get(TransactionModel, transaction_id)


async def get_balance_by_address_id(session: AsyncSession, address_id: int) -> float:
    stmt1 = select(TransactionModel.fee).where(TransactionModel.to_addr == address_id)
    stmt2 = select(TransactionModel.fee).where(TransactionModel.from_addr == address_id)
    incoming_result = sum(list(await session.scalars(stmt1)))
    outgoing_result = sum(list(await session.scalars(stmt2)))
    return incoming_result - outgoing_result


async def get_minimum_fee(session: AsyncSession) -> float:
    stmt = select(TransactionModel).order_by(TransactionModel.fee).limit(1)
    return (await session.scalar(stmt)).fee


async def get_open_transaction_by_fee(
    session: AsyncSession, fee: float = None
) -> list[TransactionModel]:
    if fee is None:
        fee = await get_minimum_fee(session)
    stmt = select(TransactionModel).where(
        TransactionModel.fee >= fee and TransactionModel.block is None
    )
    return list(await session.scalars(stmt))


async def get_blocks(session: AsyncSession) -> list[Block]:
    stmt = select(Block).order_by(Block.id)
    result: Result = await session.execute(stmt)
    blocks = result.scalars().all()
    return list(blocks)


async def get_block_by_id(session: AsyncSession, block_id: int) -> Block | None:
    return await session.get(Block, block_id)


async def update_transaction(
    session: AsyncSession,
    transaction: TransactionModel,
    transaction_update: TransactionUpdate | TransactionUpdatePartial,
    partial: bool = False,
) -> TransactionModel:
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

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.bchain.transaction import (
    Transaction as TransactionClass,
    Address as AddressClass,
)
from backend.src.bchain.block import Block as BlockClass, TransactionList

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
        if address is not None and not await get_address_by_id(
            session=session, address_id=address.id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Address with ID {address} does not exist",
            )
    temp_dict = transaction_inp.model_dump()
    fromaddr = temp_dict.pop("fromAddr")
    if fromaddr is not None:
        temp_dict["fromAddr"] = fromaddr["address"]
    toaddr = temp_dict.pop("toAddr")
    if toaddr is not None:
        temp_dict["toAddr"] = toaddr["address"]

    transaction = TransactionModel(**temp_dict)
    session.add(transaction)
    await session.commit()
    return transaction


async def create_block(session: AsyncSession, block_inp: BlockCreate) -> Block:
    temp_list = []
    for transaction in block_inp.transactionList:
        tr = await get_open_transaction_by_fee(session=session)
        if tr is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transaction {transaction} not found!",
            )
        else:
            temp_list.append(tr)
    dump = block_inp.model_dump()
    dump["transactionList"] = temp_list
    block = Block(**dump)
    session.add(block)
    await session.commit()

    return block


async def generate_block(session: AsyncSession) -> Block:
    tr = await get_open_transaction_by_fee(session=session)
    if tr is None or len(tr) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No open transactions!",
        )
    transaction_list = TransactionList(*tr)
    last_block = await get_last_block(session)
    prev_hash = last_block.hash
    block_class = BlockClass(
        id=last_block.id + 1, prevHash=prev_hash, transactionList=transaction_list
    )
    block = Block()
    block.prevHash = prev_hash
    block.hash = block_class.hash
    block.transactionList = tr
    block.nonce = block_class.data["nonce"]
    block.datastring = block_class.datastring

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
    stmt1 = select(TransactionModel.fee).where(TransactionModel.toAddr == address_id)
    stmt2 = select(TransactionModel.fee).where(TransactionModel.fromAddr == address_id)
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
        (TransactionModel.fee >= fee) & (TransactionModel.block_id is None)
    )
    return list(await session.scalars(stmt))


async def get_blocks(session: AsyncSession) -> list[Block]:
    stmt = select(Block).order_by(Block.id)
    stmt_result: Result = await session.execute(stmt)
    blocks = stmt_result.scalars().all()
    blocks_result = list(blocks)
    result = []
    for block in blocks_result:
        tr_list = []
        for tr in block.transactionList:
            if tr.fromAddr is None:
                fromaddr = None
            else:
                address = await get_address(session, tr.fromAddr)
                fromaddr = AddressModel(id=address.id, address=address.address)
            if tr.toAddr is None:
                toaddr = None
            else:
                address = await get_address(session, tr.toAddr)
                toaddr = AddressModel(id=address.id, address=address.address)
            tr_schema = tr
            tr_schema.fromAddr = fromaddr
            tr_schema.toAddr = toaddr
            tr_list.append(tr_schema)
        block_schema = block
        block_schema.transactionList = tr_list
        result.append(block_schema)
    return result


async def get_block_by_id(session: AsyncSession, block_id: int) -> Block | None:
    return await session.get(Block, block_id)


async def get_last_block(session: AsyncSession) -> Block | None:
    stmt = select(Block).order_by(Block.id.desc()).limit(1)
    block = (await session.execute(stmt)).scalar()
    temp_list = []
    for tr in block.transactionList:
        if tr.fromAddr is None:
            fromaddr = None
        else:
            address = await get_address(session, tr.fromAddr)
            fromaddr = AddressModel(id=address.id, address=address.address)
        if tr.toAddr is None:
            toaddr = None
        else:
            address = await get_address(session, tr.toAddr)
            toaddr = AddressModel(id=address.id, address=address.address)
        tr_schema = tr
        tr_schema.fromAddr = fromaddr
        tr_schema.toAddr = toaddr
        temp_list.append(tr_schema)
    dump = block
    dump.transactionList = temp_list
    return dump


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

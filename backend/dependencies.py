from typing import Annotated

from fastapi import Path, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.models import db_helper, Block, Address

import backend.crud as crud
from backend.schemas import Transaction


async def block_by_id(
    block_id: Annotated[int, Path],
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> Block:
    product = await crud.get_block_by_id(session=session, block_id=block_id)
    if product is not None:
        return product

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Block {block_id} not found!",
    )


async def address_by_id(
    address_id: Annotated[int, Path],
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> Address:
    product = await crud.get_address_by_id(session=session, address_id=address_id)
    if product is not None:
        return product

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Address {address_id} not found!",
    )


async def transaction_by_id(
    transaction_id: Annotated[int, Path],
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> Transaction:
    transaction = await crud.get_transaction_by_id(
        session=session, transaction_id=transaction_id
    )
    if transaction is not None:
        return transaction

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Transaction {transaction_id} not found!",
    )

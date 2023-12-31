from fastapi import APIRouter, status, Depends, HTTPException
from backend.schemas import Block, BlockCreate, Transaction, Address
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.models import db_helper
from backend.dependencies import block_by_id
from backend.src.bchain import (
    Address as AddressClass,
    Transaction as TransactionClass,
    TransactionList,
    Block as BlockClass,
)
import backend.crud as crud

router = APIRouter(prefix="/block", tags=["Block"])


@router.get("s/", response_model=list[Block])
async def get_blocks(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    result = await crud.get_blocks(session=session)

    return result


@router.get("/last_block/", response_model=Block)
async def get_last_block(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    result = await crud.get_last_block(session)
    return result


@router.get("/{block_id}/", response_model=Block)
async def get_block_by_id(block: Block = Depends(block_by_id)):
    return block


@router.get("/get_length")
async def get_length(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return {"chain_length": await crud.get_chain_length(session)}


@router.delete("/{block_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_block(
    block: Block = Depends(block_by_id),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> None:
    await crud.delete_block_by_id(session=session, block=block)

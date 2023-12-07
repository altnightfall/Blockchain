from fastapi import APIRouter, status, Depends
from schemas import (
    Block,
    BlockCreate,
)
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import db_helper
from dependencies import block_by_id
import crud

router = APIRouter(prefix="/block", tags=["Block"])


@router.get("/", response_model=list[Block])
async def get_blocks(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_blocks(session=session)


@router.get("/{block_id}/", response_model=Block)
async def get_block_by_id(block: Block = Depends(block_by_id)):
    return block


@router.post(
    "/",
    response_model=Block,
    status_code=status.HTTP_201_CREATED,
)
async def create_block(
    block_inp: BlockCreate,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.create_block(session=session, block_inp=block_inp)

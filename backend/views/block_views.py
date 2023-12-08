from fastapi import APIRouter, status, Depends
from backend.schemas import Block, BlockCreate, Transaction, Address
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.models import db_helper
from backend.dependencies import block_by_id
import backend.crud as crud

router = APIRouter(prefix="/block", tags=["Block"])


@router.get("s/", response_model=list[Block])
async def get_blocks(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    result = await crud.get_blocks(session=session)

    return result


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


@router.delete("/{block_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_block(
    block: Block = Depends(block_by_id),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> None:
    await crud.delete_block_by_id(session=session, block=block)

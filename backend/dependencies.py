from typing import Annotated

from fastapi import Path, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.models import db_helper, Block

import backend.crud as crud


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

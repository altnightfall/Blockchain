from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import db_helper, Block, Transaction, Address


async def create_block(session: AsyncSession, block: Block) -> Block:
    block = Block(**block.model_dump())
    session.add(block)
    await session.commit()

    return block


async def get_blocks(session: AsyncSession) -> list[Block]:
    stmt = select(Block).order_by(Block.id)
    result: Result = await session.execute(stmt)
    blocks = result.scalars().all()
    return list(blocks)


async def get_block_by_id(session: AsyncSession, block_id: int) -> Block | None:
    return await session.get(Block, block_id)

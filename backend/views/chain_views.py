from fastapi import APIRouter, status, Depends
from backend.schemas import (
    Block,
    BlockCreate,
)
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.models import db_helper
from backend.dependencies import block_by_id
import backend.crud as crud

router = APIRouter(prefix="/chain", tags=["Chain"])


@router.post("/mine/", response_model=Block)
async def mine_new_block():
    return Block(
        prevHash="balls",
        transactionList=[69, 69, 69],
        nonce=69,
        datastring="balls",
        hash="balls",
        id=69,
    )


@router.post("/sync/")
async def sync_chain_with_peers():
    pass
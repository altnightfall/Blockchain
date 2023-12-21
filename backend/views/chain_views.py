from fastapi import APIRouter, status, Depends, HTTPException
from backend.schemas import (
    Address as AddressSchema,
    AddressCreate,
    Block,
    BlockCreate,
    TransactionCreate,
    Transaction as TransactionSchema,
)
from backend.src.bchain import (
    Address as AddressClass,
    Transaction as TransactionClass,
    TransactionList,
    Block as BlockClass,
    Constants,
)
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.models import db_helper
from backend.dependencies import block_by_id
import backend.crud as crud

router = APIRouter(prefix="/chain", tags=["Chain"])


@router.post("/mine/", response_model=Block)
async def mine_new_block(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    tr = await crud.get_open_transaction_by_fee(
        session=session, limit=Constants.BlockSize()
    )
    if tr is None or len(tr) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No open transactions!",
        )
    tr_list = []
    for tr_cur in tr:
        temp_tr = TransactionClass.fromDatastring(
            datastring=tr_cur.data,
            signature=tr_cur.signature,
        )
        tr_list.append(temp_tr)
    tr_list_class = TransactionList(*tr_list)
    last_block = await crud.get_last_block(session)

    mining_block = BlockClass(
        id=last_block.id + 1, prevHash=last_block.hash, transactionList=tr_list_class
    )
    await mining_block.mine()
    try:
        mining_block.validate()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unexpected error while validating mined block: {e}",
        )
    block_dict: dict = mining_block.data.copy()
    block_dict.pop("id")
    block_dict["hash"] = mining_block.hash
    block_dict["datastring"] = mining_block.datastring
    block_dict["transactionList"] = [tr.id for tr in tr]
    block_to_create = BlockCreate(**block_dict)
    await crud.create_block(session=session, block_inp=block_to_create)
    return block_to_create


@router.get("/chain_size/")
async def get_chain_size(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return {
        "size": len(await crud.get_blocks(session=session)),
    }


@router.post("/sync/")
async def sync_chain_with_peers():
    self_chain_size = (await get_chain_size())["size"]

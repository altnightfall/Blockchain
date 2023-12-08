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
    blocks_result = await crud.get_blocks(session=session)
    result = []
    for block in blocks_result:
        tr_list = []
        for tr in block.transactionList:
            if tr.fromAddr is None:
                fromaddr = None
            else:
                address = await crud.get_address(session, tr.fromAddr)
                fromaddr = Address(id=address.id, address=address.address)
            if tr.toAddr is None:
                toaddr = None
            else:
                address = await crud.get_address(session, tr.toAddr)
                toaddr = Address(id=address.id, address=address.address)
            tr_schema = Transaction(
                id=tr.id,
                ttype=tr.ttype,
                ttimestamp=tr.ttimestamp,
                fromAddr=fromaddr,
                toAddr=toaddr,
                value=tr.value,
                fee=tr.fee,
                data=tr.data,
                msg=tr.msg,
            )
            tr_list.append(tr_schema)
        block_schema = Block(
            id=block.id,
            prevHash=block.prevHash,
            hash=block.hash,
            transactionList=tr_list,
            nonce=block.nonce,
            datastring=block.datastring,
        )
        result.append(block_schema)

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

from fastapi import APIRouter, status, Depends
from backend.schemas import (
    Transaction,
    TransactionCreate,
)
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.models import db_helper
from backend.dependencies import transaction_by_id
import backend.crud as crud

router = APIRouter(prefix="/transaction", tags=["Transaction"])


@router.post(
    "/",
    response_model=Transaction,
    status_code=status.HTTP_201_CREATED,
)
async def create_transaction(
    transaction_inp: TransactionCreate,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    temp_result = await crud.create_transaction(
        session=session, transaction_inp=transaction_inp
    )
    from_addr = await crud.get_address_by_id(
        session=session, address_id=temp_result.fromAddr
    )
    to_addr = await crud.get_address_by_id(
        session=session, address_id=temp_result.toAddr
    )
    result = Transaction(
        ttype=temp_result.ttype,
        ttimestamp=temp_result.ttimestamp,
        fromAddr=from_addr,
        toAddr=to_addr,
        value=temp_result.value,
        fee=temp_result.fee,
        data=temp_result.data,
        msg=temp_result.msg,
        id=temp_result.id,
    )
    return result


@router.get("/{transaction_id}/")
async def get_transaction_by_id(transaction: Transaction = Depends(transaction_by_id)):
    return transaction

from fastapi import APIRouter, status, Depends
from schemas import (
    Transaction,
    TransactionCreate,
)
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import db_helper
from dependencies import block_by_id
import crud

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
    return await crud.create_transaction(
        session=session, transaction_inp=transaction_inp
    )


@router.get("/{transaction_id}/")
async def get_transaction_by_id(transaction: Transaction = Depends(block_by_id)):
    return transaction

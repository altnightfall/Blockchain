from fastapi import APIRouter, status, Depends, HTTPException
from backend.schemas import (
    Address as AddressSchema,
    Transaction,
    TransactionCreate,
    TransactionUpdatePartial,
    TransactionUpdate,
)
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.models import db_helper
from backend.dependencies import transaction_by_id
import backend.crud as crud

router = APIRouter(prefix="/transaction", tags=["Transaction"])


@router.get("/", response_model=list[Transaction])
async def get_all_transactions(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_all_transactions(session)


@router.post(
    "/",
    response_model=Transaction,
    status_code=status.HTTP_201_CREATED,
)
async def create_transaction(
    transaction_inp: TransactionCreate,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    for address in [transaction_inp.fromAddr, transaction_inp.toAddr]:
        if address is not None and not await crud.get_address_by_id(
            session=session, address_id=address
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Address with ID {address} does not exist",
            )
    temp_result = await crud.create_transaction(
        session=session, transaction_inp=transaction_inp
    )
    from_addr = await crud.get_address_by_id(
        session=session, address_id=temp_result.fromAddr
    )
    from_addr = AddressSchema(id=from_addr.id, address=from_addr.address)
    to_addr = await crud.get_address_by_id(
        session=session, address_id=temp_result.toAddr
    )
    to_addr = AddressSchema(id=to_addr.id, address=to_addr.address)
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
        pkey=temp_result.pkey,
        signature=temp_result.signature,
    )
    return result


@router.get("/{transaction_id}/")
async def get_transaction_by_id(transaction: Transaction = Depends(transaction_by_id)):
    return transaction


@router.put("/{transaction_id}/")
async def update_product(
    transaction_update: TransactionUpdate,
    transaction: Transaction = Depends(transaction_by_id),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.update_transaction(
        session=session,
        transaction=transaction,
        transaction_update=transaction_update,
    )


@router.patch("/{transaction_id}/")
async def update_product_partial(
    transaction_update: TransactionUpdatePartial,
    transaction: Transaction = Depends(transaction_by_id),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.update_transaction(
        session=session,
        transaction=transaction,
        transaction_update=transaction_update,
        partial=True,
    )

from fastapi import APIRouter, status, Depends, HTTPException
from backend.schemas import (
    Address as AddressSchema,
    Transaction,
    TransactionCreate,
    TransactionUpdatePartial,
    TransactionUpdate,
    TransactionBase,
)
from backend.src.bchain import (
    Address as AddressClass,
    Transaction as TransactionClass,
    TransactionList,
    Block as BlockClass,
    TTypes,
)
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.models import db_helper
from backend.dependencies import transaction_by_id
import backend.crud as crud
from ellipticcurve import PrivateKey

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
    transaction_inp: TransactionBase,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    if transaction_inp.fromAddr:
        from_addr_db = await crud.get_address_by_id(
            session=session, address_id=transaction_inp.fromAddr
        )
    else:
        from_addr_db = None
    if transaction_inp.toAddr:
        to_addr_db = await crud.get_address_by_id(
            session=session, address_id=transaction_inp.toAddr
        )
    else:
        to_addr_db = None
    for address_id, address in zip(
        [transaction_inp.fromAddr, transaction_inp.toAddr], [from_addr_db, to_addr_db]
    ):
        if address_id is not None and not address:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Address with ID {address} does not exist",
            )

    try:
        if from_addr_db:
            ckey = PrivateKey.fromString(from_addr_db.ckey)
        elif to_addr_db:
            ckey = PrivateKey.fromString(to_addr_db.ckey)
        else:
            raise Exception("No private key available")
        pkey = ckey.publicKey()
        tr_class = TransactionClass(
            ttype=transaction_inp.ttype,
            fromAddr=AddressClass(address=from_addr_db.address),
            toAddr=AddressClass(address=to_addr_db.address),
            pkey=pkey,
            value=transaction_inp.value,
            fee=transaction_inp.fee,
            ckey=ckey,
            timestamp=transaction_inp.ttimestamp,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=f"Error validating transaction: {e}",
        )
    temp_dict = transaction_inp.model_dump()
    temp_dict["pkey"] = tr_class.data["pkey"]
    temp_dict["data"] = tr_class.datastring
    temp_dict["signature"] = tr_class.signature
    transaction_inp_create = TransactionCreate(**temp_dict)
    temp_result = await crud.create_transaction(
        session=session, transaction_inp=transaction_inp_create
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
        id=temp_result.id,
        signature=temp_result.signature,
        block_id=temp_result.block_id,
    )
    return result


@router.get("/{transaction_id}/")
async def get_transaction_by_id(transaction: Transaction = Depends(transaction_by_id)):
    return transaction


@router.put("/{transaction_id}/")
async def update_transaction(
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
async def update_transaction_partial(
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

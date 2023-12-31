from ellipticcurve import PrivateKey
from fastapi import APIRouter, status, Depends, HTTPException, status
from backend.schemas import Address, AddressCreate, AddressBalance
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.models import db_helper
from backend.dependencies import address_by_id
import backend.crud as crud
from backend.src.bchain import (
    Address as AddressClass,
    Transaction as TransactionClass,
    TransactionList,
    Block as BlockClass,
)

router = APIRouter(prefix="/address", tags=["Address"])


@router.get("/all_addresses/", response_model=list[Address])
async def get_all_addresses(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_all_addresses(session)


@router.post(
    "/",
    response_model=Address,
    status_code=status.HTTP_201_CREATED,
)
async def create_address(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    inp_ckey = PrivateKey()
    inp_address = AddressClass(pkey=inp_ckey.publicKey())
    inp_address_schema = AddressCreate(
        address=inp_address.address, ckey=inp_ckey.toString()
    )
    return await crud.create_address(session=session, address_inp=inp_address_schema)


@router.get("/{address_id}/")
async def get_address_by_id(address: Address = Depends(address_by_id)):
    return address


@router.get("/balance/{address_id}/", response_model=AddressBalance)
async def get_address_balance(
    address_id: int,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    address_result = await crud.get_address_by_id(
        session=session, address_id=address_id
    )
    if address_result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address with ID {address_id} does not exist",
        )
    balance_result = await crud.get_balance_by_address_id(
        session=session, address_id=address_id
    )
    return AddressBalance(
        address=Address(address=address_result.address, id=address_result.id),
        balance=balance_result,
    )

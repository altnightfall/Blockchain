from fastapi import APIRouter, status, Depends, HTTPException, status
from backend.schemas import Address, AddressCreate, AddressBalance
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.models import db_helper
from backend.dependencies import address_by_id
import backend.crud as crud
from backend.src.bchain.transaction import (
    Address as AddressClass,
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
    address_inp: AddressCreate,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    if not AddressClass.validate(address_inp.address):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not validate address {address_inp.address}",
        )

    if await crud.get_address(session, address_inp.address) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Address {address_inp.address} already exists",
        )
    return await crud.create_address(session=session, address_inp=address_inp)


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

from fastapi import APIRouter, status, Depends
from backend.schemas import (
    Address,
    AddressCreate,
)
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.models import db_helper
from backend.dependencies import address_by_id
import backend.crud as crud

router = APIRouter(prefix="/address", tags=["Address"])


@router.post(
    "/",
    response_model=Address,
    status_code=status.HTTP_201_CREATED,
)
async def create_address(
    address_inp: AddressCreate,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.create_address(session=session, address_inp=address_inp)


@router.get("/{address_id}/")
async def get_address_by_id(address: Address = Depends(address_by_id)):
    return address

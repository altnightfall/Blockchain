from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
import backend.crud as crud
from backend.core.models import Base, db_helper
from backend.schemas import (
    Address as AddressSchema,
    AddressCreate,
    BlockCreate,
    TransactionCreate,
    Transaction as TransactionSchema,
)
from backend.src.bchain.block import Block, Address as AddressClass
from backend.src.bchain.transaction import Transaction
from ellipticcurve import PrivateKey


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session = db_helper.get_scoped_session()
    blocks = await crud.get_blocks(session)

    if len(blocks) == 0:
        ckey1 = PrivateKey()
        pkey1 = ckey1.publicKey()
        ckey2 = PrivateKey()
        pkey2 = ckey2.publicKey()
        addr1 = AddressClass(pkey=pkey1)
        addr2 = AddressClass(pkey=pkey2)
        address1 = AddressCreate(address=addr1.address)
        await crud.create_address(session=session, address_inp=address1)
        address2 = AddressCreate(address=addr2.address)
        await crud.create_address(session=session, address_inp=address2)

        init_block: Block = Block.createInit(ckey1)

        tr: list[Transaction] = [
            init_block.getTransaction(i)
            for i in range(init_block.getTransactionListLen())
        ]
        created_tr = []
        for tr_cur in tr:
            temp_dict = tr_cur.data.copy()
            temp_dict["data"] = tr_cur.datastring
            temp_dict["ttype"] = temp_dict["ttype"].value
            if temp_dict["fromAddr"] is not None:
                address_obj = await crud.get_address(
                    session, temp_dict["fromAddr"].address
                )
                temp_dict["fromAddr"] = AddressSchema(
                    address=address_obj.address, id=address_obj.id
                )
            else:
                temp_dict["fromAddr"] = None
            if temp_dict["toAddr"] is not None:
                address_obj = await crud.get_address(
                    session, temp_dict["toAddr"].address
                )
                temp_dict["toAddr"] = AddressSchema(
                    address=address_obj.address, id=address_obj.id
                )
            else:
                temp_dict["toAddr"] = None
            temp_dict.pop("pkey")
            temp_dict["ttimestamp"] = temp_dict.pop("timestamp")
            temp_dict["block_id"] = None
            tr_to_create = TransactionCreate(**temp_dict)
            db_response = await crud.create_transaction(
                session=session, transaction_inp=tr_to_create
            )
            created_tr.append(db_response)
        block_dict: dict = init_block.data.copy()
        block_dict.pop("id")
        block_dict["hash"] = init_block.hash
        block_dict["datastring"] = init_block.datastring
        block_dict["transactionList"] = [tr.id for tr in created_tr]
        block_to_create = BlockCreate(**block_dict)
        await crud.create_block(session=session, block_inp=block_to_create)
    await session.close()

    yield

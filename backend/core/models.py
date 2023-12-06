from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    declared_attr,
    relationship,
)
from sqlalchemy import func, String, ForeignKey
from sqlalchemy.ext.asyncio import (
    async_scoped_session,
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from typing import List
from typing_extensions import Annotated
from datetime import datetime
from asyncio import current_task
from backend.core.config import settings


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}_table"

    id: Mapped[int] = mapped_column(primary_key=True)


intpk = Annotated[int, mapped_column(primary_key=True)]
timestamp = Annotated[
    datetime, mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP())
]


class Address(Base):
    address: Mapped[str] = mapped_column(String(42))


class Transaction(Base):
    ttype: Mapped[int]
    ttimestamp: Mapped[timestamp] = mapped_column(server_default=func.UTC_TIMESTAMP())
    fromAddr: Mapped[int] = mapped_column(ForeignKey("address_table.id"))
    toAddr: Mapped[int] = mapped_column(ForeignKey("address_table.id"))
    value: Mapped[int]
    data: Mapped[int]
    msg: Mapped[str]
    parentBlockID: Mapped[int] = mapped_column(
        ForeignKey("block_table.id"), nullable=True
    )
    block: Mapped["Block"] = relationship(back_populates="transactionList")


class Block(Base):
    prevHash: Mapped[str]
    transactionList: Mapped[List["Transaction"]] = relationship(back_populates="block")
    nonce: Mapped[int]
    datastring: Mapped[str]
    hash: Mapped[str]


class DatabaseHelper:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(
            url=url,
            echo=echo,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    def get_scoped_session(self):
        session = async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task,
        )
        return session

    async def scoped_session_dependency(self) -> AsyncSession:
        session = self.get_scoped_session()
        yield session
        await session.close()


db_helper = DatabaseHelper(
    url=settings.db_url,
    echo=settings.db_echo,
)

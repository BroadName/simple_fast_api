import datetime
from decimal import Decimal
import os
from uuid import UUID

from extra_types import ModelName

from sqlalchemy import Text, String, Integer, DECIMAL, DateTime, func, UUID, ForeignKey, Table, Column, Boolean, \
    UniqueConstraint, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker


POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "secret")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "advs")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5431")

PG_DSN = (
    f"postgresql+asyncpg://"
    f"{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/"
    f"{POSTGRES_DB}"
)

TOKEN_TTL = os.getenv("TOKEN_TTL", 60*60*48)

engine = create_async_engine(PG_DSN)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):
    pass


role_rights = Table(
    "role_rights_relation",
    Base.metadata,
    Column("role_id", ForeignKey("role.id"), index=True),
    Column("right_id", ForeignKey("right.id"), index=True)
)


user_roles = Table(
    "user_roles_relation",
    Base.metadata,
    Column("user_id", ForeignKey("ad_user.id", ondelete='CASCADE'), index=True),
    Column("role_id", ForeignKey("role.id", ondelete='CASCADE'), index=True)
)


class Right(Base):
    __tablename__ = 'right'
    _model = 'right'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    write: Mapped[bool] = mapped_column(Boolean, default=False)
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    only_own: Mapped[bool] = mapped_column(Boolean, default=True)
    model: Mapped[ModelName] = mapped_column(String)

    __table_args__ = (
        UniqueConstraint("model", "only_own", "read", "write"),
        CheckConstraint("model in ('user', 'advertisement', 'right', 'role')")
    )


class Role(Base):
    __tablename__ = 'role'
    _model = 'role'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    rights: Mapped[list[Right]] = relationship(secondary=role_rights, lazy='joined')


class User(Base):
    __tablename__ = 'ad_user'
    _model = 'user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    tokens: Mapped[list["Token"]] = relationship("Token", back_populates="user", lazy="joined", cascade='all, delete')
    ads: Mapped[list["Advertisement"]] = relationship("Advertisement", back_populates="user", lazy="joined")
    roles: Mapped[list["Role"]] = relationship(secondary=user_roles, lazy='joined')

    @property
    def dict(self):
        return {"id": self.id,
                "name": self.name,
                "ads": self.ads}


class Token(Base):
    __tablename__ = 'token'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[UUID] = mapped_column(UUID, server_default=func.gen_random_uuid(), unique=True)
    creation_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("ad_user.id"), onupdate='')
    user: Mapped[User] = relationship("User", lazy="joined", back_populates="tokens")


class Advertisement(Base):
    __tablename__ = 'advertisement'
    _model = 'advertisement'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[Decimal] = mapped_column(DECIMAL(precision=10, scale=2))
    author: Mapped[str] = mapped_column(String(100))
    created_date: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("ad_user.id"))
    user: Mapped[User] = relationship("User", lazy="joined", back_populates="ads")

    @property
    def dict(self):
        return {
            "id": self.id,
            "author": self.author,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "created_date": self.created_date,
            "user_id": self.user_id
            }


ORM_OBJECT = Advertisement | User | Token
ORM_CLS = type[Advertisement] | type[User] | type[Token]

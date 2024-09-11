import datetime
import uuid

from typing import Literal

from pydantic import BaseModel


class StatusResponse(BaseModel):
    status: Literal["ok", "deleted"]


class ItemId(BaseModel):
    id: int


class GetAdv(BaseModel):
    id: int
    title: str
    author: str
    description: str
    price: float
    created_date: datetime.datetime
    user_id: int


class CreateAdv(BaseModel):
    title: str
    author: str
    description: str
    price: float


class UpdateAdv(BaseModel):
    title: str | None = None
    author: str | None = None
    description: str | None = None
    price: float | None = None


class BaseUser(BaseModel):
    name: str
    password: str


class CreateUser(BaseUser):
    pass


class Login(BaseUser):
    pass


class LoginResponse(BaseModel):
    token: uuid.UUID


class GetUser(BaseUser):
    password: str | None = None


class UpdateUser(BaseModel):
    name: str | None = None
    password: str | None = None

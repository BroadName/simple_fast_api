import datetime

from typing import Literal

from pydantic import BaseModel


class StatusResponse(BaseModel):
    status: Literal["ok", "deleted"]


class AdvId(BaseModel):
    id: int


class GetAdv(BaseModel):
    id: int
    title: str
    author: str
    description: str
    price: float
    created_date: datetime.datetime


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

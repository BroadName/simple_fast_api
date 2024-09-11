from typing import List

from models import Session, ORM_CLS, ORM_OBJECT
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from fastapi import HTTPException


async def add_item(session: Session, item: ORM_OBJECT) -> ORM_OBJECT:
    session.add(item)
    try:
        await session.commit()
    except IntegrityError as err:
        if err.orig.pgcode == "23505":
            raise HTTPException(status_code=409, detail="Item already exists")
        raise err
    return item


async def get_item(session: Session, orm_cls: ORM_CLS, item_id: int) -> ORM_OBJECT:
    orm_obj = await session.get(orm_cls, item_id)
    if orm_obj is None:
        raise HTTPException(status_code=404, detail=f"{orm_cls.__name__} not found")
    return orm_obj


async def get_search_items(session: Session, orm_cls: ORM_CLS, field: str, search_word: str) -> List[ORM_OBJECT]:
    filter_expr = getattr(orm_cls, field).like(f"%{search_word}%")
    stmt = select(orm_cls).filter(filter_expr)
    results = await session.execute(stmt)
    orm_objects = results.unique().scalars().all()
    if not orm_objects:
        raise HTTPException(status_code=404, detail='There are no matches')
    return orm_objects

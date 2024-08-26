import fastapi

from typing import List
from description import DESCRIPTION
from models import Advertisement
from schema import CreateAdv, AdvId, GetAdv, UpdateAdv, StatusResponse
from lifespan import lifespan
from dependencies import SessionDependency
import crud


app = fastapi.FastAPI(
    title='Advertisements API',
    version="0.0.1",
    description=DESCRIPTION,
    lifespan=lifespan
)


@app.get("/v1/advs/search", response_model=List[GetAdv])
async def search_advs(field: str, search_word: str, session: SessionDependency):
    advs = await crud.get_search_items(session, Advertisement, field, search_word)
    results = [adv.dict for adv in advs if adv is not None]
    return results


@app.get("/v1/advs/{adv_id}", response_model=GetAdv)
async def get_adv(adv_id: int, session: SessionDependency):
    adv = await crud.get_item(session, Advertisement, adv_id)
    return adv.dict


@app.post("/v1/advs", response_model=AdvId)
async def create_adv(adv: CreateAdv, session: SessionDependency):
    adv = Advertisement(**adv.dict())
    adv = await crud.add_item(session, adv)
    return {"id": adv.id}


@app.patch("/v1/advs/{adv_id}", response_model=AdvId)
async def update_adv(adv_id: int, adv: UpdateAdv, session: SessionDependency):
    adv_origin = await crud.get_item(session, Advertisement, adv_id)
    for field, value in adv.dict(exclude_unset=True).items():
        setattr(adv_origin, field, value)
    adv_origin = await crud.add_item(session, adv_origin)
    return {"id": adv_origin.id}


@app.delete("/v1/advs/{adv_id}", response_model=StatusResponse)
async def delete_adv(adv_id: int, session: SessionDependency):
    adv = await crud.get_item(session, Advertisement, adv_id)
    await session.delete(adv)
    await session.commit()
    return {"status": "deleted"}

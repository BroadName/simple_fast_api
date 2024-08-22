import fastapi

from description import DESCRIPTION

from schema import CreateAdv, AdvId, GetAdv, UpdateAdv, StatusResponse
from lifespan import lifespan



app = fastapi.FastAPI(
    title='Advertisements API',
    version="0.0.1",
    description=DESCRIPTION,
    lifespan=lifespan
)


@app.get("/v1/advs/{adv_id}", response_model=GetAdv)
async def get_adv(adv_id: int):

    return {}


@app.post("/v1/advs", response_model=AdvId)
async def create_adv(adv: CreateAdv):

    return {}


@app.patch("/v1/advs/{adv_id}", response_model=GetAdv)
async def update_adv(adv_id: int, adv: UpdateAdv):

    return {}


@app.delete("/v1/advs/{adv_id}", response_model=StatusResponse)
async def delete_adv(adv_id: int):

    return {"status": "deleted"}

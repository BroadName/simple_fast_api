import fastapi

from typing import List

from sqlalchemy import select

from description import DESCRIPTION
from models import Advertisement, User, Token
from schema import CreateAdv, ItemId, GetAdv, UpdateAdv, StatusResponse, CreateUser, Login, LoginResponse, GetUser, \
    UpdateUser
from lifespan import lifespan
from dependencies import SessionDependency, TokenDependency
import crud
import auth


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


@app.post("/v1/advs", response_model=ItemId)
async def create_adv(adv: CreateAdv, session: SessionDependency, token: TokenDependency):
    user_id = token.user_id
    adv = Advertisement(**adv.dict(), user_id=user_id)
    await auth.check_access_rights(session,
                                   token,
                                   adv,
                                   write=True,
                                   read=False,
                                   )
    adv = await crud.add_item(session, adv)
    return {"id": adv.id}


@app.patch("/v1/advs/{adv_id}", response_model=ItemId)
async def update_adv(adv_id: int, adv: UpdateAdv, session: SessionDependency, token: TokenDependency):
    adv_origin = await crud.get_item(session, Advertisement, adv_id)
    await auth.check_access_rights(session,
                                   token,
                                   adv_origin,
                                   write=True,
                                   read=False,
                                   )
    for field, value in adv.dict(exclude_unset=True).items():
        setattr(adv_origin, field, value)
    adv_origin = await crud.add_item(session, adv_origin)
    return {"id": adv_origin.id}


@app.delete("/v1/advs/{adv_id}", response_model=StatusResponse)
async def delete_adv(adv_id: int, session: SessionDependency, token: TokenDependency):

    adv = await crud.get_item(session, Advertisement, adv_id)
    await auth.check_access_rights(session,
                                   token,
                                   adv,
                                   write=True,
                                   read=False,
                                   )
    await session.delete(adv)
    await session.commit()
    return {"status": "deleted"}


@app.post("/v1/user", response_model=ItemId)
async def create_user(user_data: CreateUser, session: SessionDependency):
    user = User(**user_data.dict())
    user.password = auth.hash_password(user.password)
    user.roles = [(await auth.get_default_role(session)), ]
    user = await crud.add_item(session, user)
    return {'id': user.id}


@app.get("/v1/user/{user_id}", response_model=GetUser)
async def get_user(user_id: int, session: SessionDependency):
    user = await crud.get_item(session, User, user_id)
    return user.dict


@app.patch("/v1/user/{user_id}", response_model=ItemId)
async def update_user(user_id: int, user: UpdateUser, session: SessionDependency, token: TokenDependency):
    user_origin = await crud.get_item(session, User, user_id)
    await auth.check_access_rights(session,
                                   token,
                                   user_origin,
                                   write=True,
                                   read=False,
                                   )
    if user.password:
        user.password = auth.hash_password(user.password)
    for field, value in user.dict(exclude_unset=True).items():
        setattr(user_origin, field, value)
    adv_origin = await crud.add_item(session, user_origin)
    return {"id": adv_origin.id}


@app.delete("/v1/user/{user_id}", response_model=StatusResponse)
async def delete_user(user_id: int, session: SessionDependency, token: TokenDependency):
    user = await crud.get_item(session, User, user_id)
    await auth.check_access_rights(session,
                                   token,
                                   user,
                                   write=True,
                                   read=False,
                                   )
    await session.delete(user)
    await session.commit()
    return {"status": "deleted"}


@app.post("/v1/login", response_model=LoginResponse)
async def login(login_data: Login, session: SessionDependency):
    user_query = select(User).where(User.name == login_data.name)
    user_model = await session.scalar(user_query)

    if user_model is None:
        raise fastapi.HTTPException(401, "Invalid user or password")

    if not auth.check_password(login_data.password, user_model.password):
        raise fastapi.HTTPException(401, "Invalid user or password")

    token = Token(user_id=user_model.id)
    token = await crud.add_item(session, token)
    return {"token": token.token}

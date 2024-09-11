import datetime
import uuid

import fastapi
from sqlalchemy import select

from models import Session, Token, TOKEN_TTL
from typing import Annotated
from fastapi import Depends, Header


async def get_session():
    async with Session() as session:
        return session

SessionDependency = Annotated[Session, Depends(get_session, use_cache=True)]


async def get_token(x_token: Annotated[uuid.UUID, Header()], session: SessionDependency):
    token_query = select(Token).where(Token.token == x_token,
                                      Token.creation_time >=
                                      datetime.datetime.now() - datetime.timedelta(seconds=TOKEN_TTL)
                                      )
    token = (await session.scalar(token_query))
    if token is not None:
        return token
    return fastapi.HTTPException(401, "Invalid token")


TokenDependency = Annotated[Token, Depends(get_token)]

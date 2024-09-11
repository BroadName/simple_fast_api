import bcrypt
import fastapi
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models import Role, ORM_OBJECT, ORM_CLS, Token, User, Right


def hash_password(password: str) -> str:
    password = password.encode()
    password = bcrypt.hashpw(password, bcrypt.gensalt())
    password = password.decode()
    return password


def check_password(password: str, hashed_password: str) -> bool:
    password = password.encode()
    hashed_password = hashed_password.encode()
    return bcrypt.checkpw(password, hashed_password)


async def get_default_role(session: AsyncSession) -> Role:
    query = select(Role).where(Role.name == "user")
    role = await session.scalar(query)
    return role


async def check_access_rights(session: AsyncSession,
                              token: Token,
                              model: ORM_OBJECT | ORM_CLS,
                              write: bool,
                              read: bool,
                              owner_field: str = "user_id",
                              raise_exception: bool = True
                              ) -> bool:
    where_args = [User.id == Token.user_id, Right.model == model._model]

    if write:
        where_args.append(Right.write == True)
    if read:
        where_args.append(Right.read == True)

    if (hasattr(model, owner_field)) and getattr(model, owner_field) != token.user_id:
        where_args.append(Right.only_own == False)

    right_query = (
        select(func.count(User.id)).
        join(Role, User.roles).
        join(Right, Role.rights).
        where(*where_args)
    )
    right_count = await session.scalar(right_query)
    if not right_count and raise_exception:
        raise fastapi.HTTPException(status_code=403, detail="Access denied")
    return right_count > 0

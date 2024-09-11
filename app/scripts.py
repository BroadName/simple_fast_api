from sqlalchemy.ext.asyncio.session import AsyncSession
import asyncio
from models import Advertisement, User, Right, Role, Session


async def create_default_role(session: AsyncSession):
    rights = []

    for wr in True, False:
        for model in User, Advertisement:
            rights.append(
                Right(
                    model=model._model,
                    only_own=True,
                    read=wr,
                    write=not wr
                )
            )
    role = Role(name='user', rights=rights)
    session.add_all([*rights, role])
    await session.commit()


async def create_admin_role(session: AsyncSession):
    rights = []
    for model in User, Advertisement:
        rights.append(
            Right(
                model=model._model,
                only_own=True,
                read=True,
                write=True
            )
        )
    role = Role(name='admin', rights=rights)
    session.add_all([*rights, role])
    await session.commit()


async def main():
    async with Session() as session:
        await create_default_role(session)
        await create_admin_role(session)


if __name__ == "__main__":
    asyncio.run(main())

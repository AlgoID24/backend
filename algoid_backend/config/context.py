from graphql import GraphQLError
import jwt
from typing import Optional
from sqlalchemy import select
import strawberry
from strawberry.fastapi import BaseContext

from algoid_backend.config.db import sessionmanager
from algoid_backend.apps.users.models.users import User
from algoid_backend.config.settings import settings


class Context(BaseContext):
    async def user(self) -> Optional[User]:
        if not self.request:
            return None
        print(self.request.headers)
        authorization = self.request.headers.get("Authorization")

        if not authorization:
            return None

        decoded = jwt.decode(
            authorization.split(" ").pop(), settings.secret_key, ["HS256"]
        )
        decoded = dict(decoded)
        user_id = decoded.get("user_id")
        if not user_id:
            return None

        async with sessionmanager.session() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()

    async def ensure_user(self) -> User:
        user = await self.user()
        assert user, GraphQLError("You must be authenticated to perform this action")

        return user


Info = strawberry.Info[Context]


def get_context() -> Context:
    return Context()

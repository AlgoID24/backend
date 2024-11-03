import uuid
from sqlalchemy import select
import strawberry
from datetime import datetime
from typing import TYPE_CHECKING, Annotated, Self
from algoid_backend.config.db import sessionmanager


if TYPE_CHECKING:
    from algoid_backend.apps.users.models.auth import AuthToken
    from algoid_backend.apps.users.graphql.types.outputs.users import UserType

LazyUserType = Annotated[
    "UserType", strawberry.lazy("algoid_backend.apps.users.graphql.types.outputs.users")
]


@strawberry.type
class AuthTokenType:
    id: uuid.UUID
    token: str
    user_id: strawberry.Private[uuid.UUID]
    date_added: datetime
    last_updated: datetime

    @strawberry.field
    async def user(self) -> LazyUserType:
        from .users import User
        from algoid_backend.apps.users.graphql.types.outputs.users import UserType

        async with sessionmanager.session() as session:
            result = await session.execute(select(User).where(User.id == self.user_id))
            user = result.scalar_one()
            return UserType.from_model(user)

    @classmethod
    def from_model(cls, model: "AuthToken") -> Self:
        return cls(
            id=model.id,
            token=model.token,
            user_id=model.user_id,
            date_added=model.date_added,
            last_updated=model.last_updated,
        )

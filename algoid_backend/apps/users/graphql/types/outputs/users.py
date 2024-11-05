import uuid
from sqlalchemy import select
import strawberry
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional, Self, cast

from algoid_backend.config.db import sessionmanager
from algoid_backend.apps.common.graphql.types.scalars import JSON

if TYPE_CHECKING:
    from algoid_backend.apps.users.models.users import User, Profile


@strawberry.type
class UserType:
    id: uuid.UUID
    email: str
    date_added: datetime
    last_updated: datetime

    @classmethod
    def from_model(cls, model: "User") -> Self:
        return cls(
            id=model.id,
            email=model.email,
            date_added=model.date_added,
            last_updated=model.last_updated,
        )


@strawberry.type
class ProfileType:
    id: uuid.UUID
    first_name: Optional[str]
    last_name: Optional[str]
    nin: Optional[str]
    face_recognition: Optional[JSON]
    verified: bool
    user_id: strawberry.Private[uuid.UUID]
    date_added: datetime
    last_updated: datetime

    @strawberry.field
    async def user(self) -> UserType:
        from algoid_backend.apps.users.models.users import User

        async with sessionmanager.session() as session:
            result = await session.execute(select(User).where(User.id == self.user_id))
            return UserType.from_model(result.scalar_one())

    @classmethod
    def from_model(cls, model: "Profile") -> Self:
        return cls(
            id=model.id,
            first_name=model.first_name,
            last_name=model.last_name,
            nin=model.nin,
            face_recognition=cast(Any, model.face_recognition),
            verified=model.verified,
            user_id=model.user_id,
            date_added=model.date_added,
            last_updated=model.last_updated,
        )


@strawberry.type
class UpdateProfileResponse:
    profile: ProfileType
    did: JSON

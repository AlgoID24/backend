from typing import Any, Dict, cast
from graphql import GraphQLError
from sqlalchemy import select
import strawberry

from algoid_backend.apps.common.graphql.types.output import Response, ResponseStatus
from algoid_backend.apps.users.graphql.types.outputs.users import ProfileType
from algoid_backend.config.db import sessionmanager
from algoid_backend.apps.users.graphql.types.input.users import UserProfileInput
from algoid_backend.apps.users.models.users import Profile
from algoid_backend.config.context import Info


@strawberry.type
class UsersMutations:
    @strawberry.mutation
    async def update_user_profile(
        self, info: Info, input: UserProfileInput
    ) -> Response[ProfileType]:
        async with sessionmanager.session() as session:
            user = await info.context.ensure_user()
            assert user.id == input.user_id, GraphQLError(
                "You are not authorized to perform this action"
            )
            profile_res = await session.execute(
                select(Profile).where(Profile.user_id == user.id)
            )
            profile = profile_res.scalar_one_or_none()
            if not profile:
                profile = Profile(user_id=user.id)

            profile.first_name = input.first_name
            profile.last_name = input.last_name
            profile.nin = input.nin
            profile.face_recognition = cast(Dict[str, Any], input.face_recognition)

            session.add(profile)
            await session.commit()
            await session.refresh(profile)

            return Response[ProfileType](
                status=ResponseStatus.SUCCESS,
                message="Profile updated successfully",
                data=ProfileType.from_model(profile),
            )

from datetime import datetime
import jwt
import bcrypt
from sqlalchemy import select
import strawberry
from graphql import GraphQLError

from algoid_backend.apps.common.graphql.types.output import Response, ResponseStatus
from algoid_backend.apps.users.graphql.types.input.auth import (
    EmailPasswordSignInInput,
    EmailPasswordSignUpInput,
)
from algoid_backend.apps.users.graphql.types.outputs.auth import AuthTokenType
from algoid_backend.apps.users.models.auth import AuthToken
from algoid_backend.apps.users.models.users import User
from algoid_backend.config.settings import settings
from algoid_backend.config.db import sessionmanager


@strawberry.type
class UsersAuthMutations:
    @strawberry.mutation
    async def email_password_signup(
        self, input: EmailPasswordSignUpInput
    ) -> Response[None]:
        async with sessionmanager.session() as session:
            assert input.password_1 == input.password_2, GraphQLError(
                "Passwords do not match"
            )
            password_hash = bcrypt.hashpw(
                input.password_1.encode(), bcrypt.gensalt()
            ).decode()
            user = User(email=input.email, password_hash=password_hash)
            session.add(user)
            await session.commit()
            await session.refresh(user)

            return Response[None](
                status=ResponseStatus.SUCCESS,
                message="A verification email has been sent to the provided email",
                data=None,
            )

    @strawberry.mutation
    async def email_password_signin(
        self, input: EmailPasswordSignInInput
    ) -> Response[AuthTokenType]:
        async with sessionmanager.session() as session:
            result = await session.execute(
                select(User).where(User.email == input.email)
            )
            user = result.scalar_one_or_none()
            assert user, GraphQLError("User not found")
            assert user.password_hash, GraphQLError("Password login not found for user")

            assert bcrypt.checkpw(
                input.password.encode(), user.password_hash.encode()
            ), GraphQLError("Incorrect email or password")

            auth_token_result = await session.execute(
                select(AuthToken).where(AuthToken.user_id == user.id)
            )
            auth_token = auth_token_result.scalar_one_or_none()
            if auth_token:
                await session.delete(auth_token)
                await session.commit()
            token_data = {
                "exp": datetime.now() + settings.auth_token_token_valid_duration,
                "email": user.email,
                "user_id": str(user.id),
            }
            token = jwt.encode(token_data, settings.secret_key.encode(), "HS256")
            auth_token = AuthToken(token=token, user_id=user.id)
            session.add(auth_token)
            await session.commit()
            await session.refresh(auth_token)

            return Response[AuthTokenType](
                status=ResponseStatus.SUCCESS,
                message="SignIn success",
                data=AuthTokenType.from_model(auth_token),
            )

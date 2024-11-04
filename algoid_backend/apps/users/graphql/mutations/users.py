# import hashlib
from typing import Any, Dict, Tuple, cast

# from algosdk import transaction
from graphql import GraphQLError
from sqlalchemy import select
import strawberry

# from algoid_backend.apps.common.contract import Contract
from algoid_backend.apps.common.graphql.types.output import Response, ResponseStatus
from algoid_backend.apps.common.graphql.types.scalars import JSON
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
    ) -> Response[Tuple[ProfileType, JSON]]:
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

            did, did_document, private_key = await profile.create_did_document()
            user_info_vc = await profile.create_verifiable_credential(
                "IdentityClaims",
                {
                    "email": user.email,
                    "firstName": profile.first_name,
                    "lastName": profile.last_name,
                    "nin": profile.nin,
                    "faceRecognition": profile.face_recognition,
                },
            )

            # sha256_hash = hashlib.sha256(str(profile.id).encode()).hexdigest()[:8]
            #
            # result = Contract.authentication_client().create_algo_id(
            #     unit_name=f"ALG-{sha256_hash}",
            #     full_name=f"{profile.first_name} {profile.last_name}",
            #     metadata_url=f"https://aqua-tricky-mammal-620.mypinata.cloud/ipfs/{profile.ipfs_hash}",
            # )
            #
            # sp = Contract.authentication_client().algod_client.suggested_params()
            #
            # optin_txn = transaction.AssetOptInTxn(
            #     sender=Contract.live_account().address, sp=sp, index=result.return_value
            # )
            #
            # optin_txn = optin_txn.sign(Contract.live_account().private_key)
            #
            # txn_id = Contract.authentication_client().algod_client.send_transaction(
            #     optin_txn
            # )
            # transaction.wait_for_confirmation(
            #     Contract.authentication_client().algod_client,
            #     txid=txn_id,
            #     wait_rounds=4,
            # )
            #
            # result2 = Contract.authentication_client().tranfer_algo_id_token(
            #     user_address=Contract.live_account().address, asset=result.return_value
            # )

            return Response[Tuple[ProfileType, JSON]](
                status=ResponseStatus.SUCCESS,
                message="Profile updated successfully",
                data=(
                    ProfileType.from_model(profile),
                    cast(
                        JSON,
                        {
                            "did": did,
                            "did_document": did_document,
                            "private_key": private_key,
                            "user_info_vc": user_info_vc,
                        },
                    ),
                ),
            )

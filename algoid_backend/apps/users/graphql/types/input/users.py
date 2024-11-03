import uuid
import strawberry

from algoid_backend.apps.common.graphql.types.scalars import JSON


@strawberry.input
class UserProfileInput:
    user_id: uuid.UUID
    first_name: str
    last_name: str
    face_recognition: JSON
    nin: str

import strawberry

from algoid_backend.apps.users.graphql.mutations.users import UsersMutations
from algoid_backend.apps.users.graphql.mutations.auth import UsersAuthMutations


@strawberry.type
class Mutation(UsersMutations, UsersAuthMutations):
    pass


@strawberry.type
class Query:
    @strawberry.field
    def version(self) -> str:
        return "0.0.1"


schema = strawberry.Schema(query=Query, mutation=Mutation)

from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from algoid_backend.config.context import get_context
from algoid_backend.config.schema import schema


graphql_app = GraphQLRouter(schema=schema, context_getter=get_context)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

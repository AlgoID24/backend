from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from fastapi.middleware.cors import CORSMiddleware

from algoid_backend.config.settings import settings
from algoid_backend.config.context import get_context
from algoid_backend.config.schema import schema


graphql_app = GraphQLRouter(schema=schema, context_getter=get_context)

ALLOWED_HOSTS = settings.allowed_hosts.split(",")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(graphql_app, prefix="/graphql")

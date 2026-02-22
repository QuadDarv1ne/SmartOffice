"""
GraphQL API Router
"""

from fastapi import APIRouter, Request
from strawberry.fastapi import GraphQLRouter
from app.graphql.schema import schema

# GraphQL endpoint
graphql_router = GraphQLRouter(
    schema,
    graphiql=True,  # Включить GraphiQL интерфейс
    allow_queries_via_get=True,
)

router = APIRouter()
router.include_router(graphql_router, prefix="/graphql")

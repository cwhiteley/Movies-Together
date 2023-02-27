import uvicorn
import logging
from redis import asyncio as aioredis
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import groups
from db import redis
from core.config import settings

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="API for service view together",
    version="1.0.0",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    redis.redis_conn = await aioredis.Redis(
            host=settings.redis.host, port=settings.redis.port, decode_responses=True
        )
    logging.info("Create connections")


@app.on_event("shutdown")
async def shutdown():
    if redis.redis_conn is not None:
        redis.redis_conn.close()
        await redis.redis_conn.wait_closed()
    logging.info("Closed connections")


app.include_router(groups.router, prefix="/api/v1/groups", tags=["Group views"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app", host=settings.base_api.host, port=settings.base_api.port, reload=True
    )
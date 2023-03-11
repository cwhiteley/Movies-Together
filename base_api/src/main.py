import json
import logging

import backoff
import redis as redis_bibl
import uvicorn
from api.v1 import groups, stream, search, auth
from core.config import settings
from db import redis_cache
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles
from redis import asyncio as aioredis
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="API for service view together",
    version="1.0.0",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
@backoff.on_exception(
    backoff.expo,
    (redis_bibl.exceptions.ConnectionError),
    max_time=1000,
    max_tries=10,
)
async def startup():
    redis_cache.redis_conn = await aioredis.Redis(
        host=settings.redis.host, port=settings.redis.port, decode_responses=True
    )
    await redis_cache.redis_conn.ping()

    logging.info("Create connections")


@app.on_event("shutdown")
async def shutdown():
    if redis_cache.redis_conn is not None:
        await redis_cache.redis_conn.close()
    logging.info("Closed connections")


app.include_router(groups.router, prefix="/api/v1/groups", tags=["Group views"])
app.include_router(stream.router, prefix="/api/v1/stream", tags=["Stream film"])
app.include_router(search.router, prefix="/api/v1/movies", tags=["Search film"])
app.include_router(auth.router, prefix="/api/v1", tags=["Auth"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host='0.0.0.0',
        # host=settings.base_api.host,
        port=settings.base_api.port,
        reload=True,
    )

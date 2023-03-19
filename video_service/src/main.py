import logging

import backoff
import redis
import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1.control import router
from core.config import settings
from db.cache import get_redis_client

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="API for group video",
    version="1.0.0",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
@backoff.on_exception(
    backoff.expo,
    (redis.exceptions.ConnectionError),
    max_time=1000,
    max_tries=10,
)
async def startup():
    redis_client = await get_redis_client()
    redis_conn = await redis_client._get_redis()
    await redis_conn.ping()

    logging.info("Create connections")


@app.on_event("shutdown")
async def shutdown():
    redis_client = await get_redis_client()
    await redis_client.close()
    logging.info("Closed connections")


app.include_router(router, tags=["video"])
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.video_service.host,
        # port=settings.chat_service.port,
        port=8002,
        reload=True,
    )

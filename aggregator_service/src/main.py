import logging

import backoff
import redis as redis_bibl
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from redis import asyncio as aioredis

from api.v1 import control
from api.v1 import groups, stream, search, auth
from core.config import ROOT_PATH
from core.config import settings
from db import cache_db

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="API for service view together",
    version="1.0.0",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)
templates = Jinja2Templates(directory="templates")

if settings.debug:
    app.mount("/static", StaticFiles(directory="static"), name="static")
else:
    app.mount("/static", StaticFiles(directory=f"{ROOT_PATH}static"), name="static")


@app.on_event("startup")
@backoff.on_exception(
    backoff.expo,
    (redis_bibl.exceptions.ConnectionError),
    max_time=1000,
    max_tries=10,
)
async def startup():
    cache_db.redis_conn = await aioredis.Redis(
        host=settings.redis.host, port=settings.redis.port, decode_responses=True
    )
    await cache_db.redis_conn.ping()

    logging.info("Create connections")


@app.on_event("shutdown")
async def shutdown():
    if cache_db.redis_conn is not None:
        await cache_db.redis_conn.close()
    logging.info("Closed connections")


origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    if exc.status_code == 401:
        return templates.TemplateResponse("login_problem.html", {"request": request})
    return exc


app.include_router(groups.router, prefix="/api/v1/groups", tags=["Group views"])
app.include_router(stream.router, prefix="/api/v1/stream", tags=["Stream film"])
app.include_router(search.router, prefix="/api/v1/movies", tags=["Search film"])
app.include_router(
    control.router, prefix="/api/v1/control", tags=["Control panel for owner"]
)
app.include_router(auth.router, prefix="/api/v1", tags=["Auth"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        # host=settings.aggregator_service.host,
        port=settings.base_api.port,
        reload=True,
    )

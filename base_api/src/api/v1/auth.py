import os
from fastapi.responses import FileResponse
from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
import requests
from core.config import settings, ROOT_PATH

router = APIRouter()

templates = Jinja2Templates(directory=f"{ROOT_PATH}templates")


@router.get(
    "/register",
)
async def register(request: Request):
    return templates.TemplateResponse(
        "register.html", {"request": request, "server_host": settings.server_host}
    )


@router.get(
    "/login",
)
async def login(request: Request):
    return templates.TemplateResponse(
        "login.html", {"request": request, "server_host": settings.server_host}
    )

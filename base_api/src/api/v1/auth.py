from fastapi.responses import FileResponse
from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
import requests
from core.config import settings

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get(
    "/register",
)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get(
    "/login",
)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

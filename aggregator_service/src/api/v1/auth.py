from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from core.config import ROOT_PATH, settings

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

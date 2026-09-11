"""Telegram Bot Handlers."""
from aiogram import Router
from .start import router as start_router
from .instances import router as instances_router
from .templates import router as templates_router
from .search_rent import router as search_rent_router
from .account import router as account_router


def setup_routers() -> Router:
    main_router = Router()
    main_router.include_router(start_router)
    main_router.include_router(instances_router)
    main_router.include_router(templates_router)
    main_router.include_router(search_rent_router)
    main_router.include_router(account_router)
    return main_router

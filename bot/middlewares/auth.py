import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

logger = logging.getLogger(__name__)


class AdminAuthMiddleware(BaseMiddleware):
    def __init__(self, admin_ids: list[int]):
        super().__init__()
        self.admin_ids = set(admin_ids)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = None
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user

        if not user:
            return await handler(event, data)

        if user.id not in self.admin_ids:
            logger.warning("Unauthorized access attempt by user_id=%s username=%s", user.id, user.username)
            if isinstance(event, Message):
                await event.answer(
                    f"⛔ <b>Доступ запрещен</b>\n\n"
                    f"Ваш Telegram ID: <code>{user.id}</code>\n"
                    f"Добавьте этот ID в <code>ADMIN_IDS</code> в файле <code>.env</code> для доступа.",
                    parse_mode="HTML",
                )
            elif isinstance(event, CallbackQuery):
                await event.answer("⛔ Доступ запрещен!", show_alert=True)
            return

        return await handler(event, data)

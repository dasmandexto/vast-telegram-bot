import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from ..api.vast_client import VastApiClient
from ..utils.formatters import format_account_card
from ..keyboards.common_kb import get_back_to_main_kb

logger = logging.getLogger(__name__)
router = Router()


async def show_account_info(target: Message | CallbackQuery, vast_client: VastApiClient):
    try:
        user_info = await vast_client.get_user_info()
        instances = await vast_client.get_instances()
        
        # Calculate active hourly burn rate (only running or loading instances)
        active_instances = [i for i in instances if i.is_running or i.is_loading]
        total_burn_rate = sum(i.dph_total for i in active_instances)

        text = format_account_card(user_info, total_burn_rate)
    except Exception as e:
        logger.error("Error fetching account info: %s", e)
        text = f"❌ <b>Ошибка при получении данных аккаунта:</b>\n<code>{e}</code>"

    if isinstance(target, CallbackQuery):
        await target.message.edit_text(text, parse_mode="HTML", reply_markup=get_back_to_main_kb())
        await target.answer()
    else:
        await target.answer(text, parse_mode="HTML", reply_markup=get_back_to_main_kb())


@router.message(Command("balance"))
async def cmd_balance(message: Message, vast_client: VastApiClient):
    await show_account_info(message, vast_client)


@router.callback_query(F.data == "menu:account")
async def cb_account_menu(call: CallbackQuery, vast_client: VastApiClient):
    await show_account_info(call, vast_client)

import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from ..api.vast_client import VastApiClient
from ..api.models import SearchFilters
from ..utils.formatters import format_offer_card
from ..keyboards.search_kb import get_templates_menu_kb, get_offers_list_kb
from ..keyboards.common_kb import get_back_to_main_kb

logger = logging.getLogger(__name__)
router = Router()

TEMPLATES_INFO = (
    "⚡ <b>Быстрые шаблоны GPU для аренды в 1 клик</b>\n\n"
    "Выберите нужный шаблон конфигурации:\n"
    "• 🟢 <b>RTX 4090</b> — 1x (24GB), 4x (96GB), 8x (192GB VRAM)\n"
    "• 🔵 <b>RTX 4080</b> — 1x (16GB), 4x (64GB), 8x (128GB VRAM)\n"
    "• 🟣 <b>Кластеры</b> — мульти-GPU ноды (4x / 8x карт)\n"
    "• 💰 <b>Бюджетный поиск</b> — видеокарты дешевле $0.35/час\n\n"
    "Бот моментально подберет самые выгодные и надежные предложения на бирже Vast.ai."
)


@router.message(Command("templates"))
async def cmd_templates(message: Message):
    await message.answer(TEMPLATES_INFO, parse_mode="HTML", reply_markup=get_templates_menu_kb())


@router.callback_query(F.data == "menu:templates")
async def cb_templates_menu(call: CallbackQuery):
    await call.message.edit_text(TEMPLATES_INFO, parse_mode="HTML", reply_markup=get_templates_menu_kb())
    await call.answer()


@router.callback_query(F.data.startswith("tmpl:"))
async def cb_handle_template_search(call: CallbackQuery, vast_client: VastApiClient):
    parts = call.data.split(":")
    category = parts[1]
    count = int(parts[2])

    filters = SearchFilters()
    title = ""

    if category == "rtx4090":
        filters.gpu_name = "RTX 4090"
        filters.min_gpus = count
        filters.max_gpus = count
        title = f"🟢 <b>Топ предложения: RTX 4090 ({count}x GPU)</b>"
    elif category == "rtx4080":
        filters.gpu_name = "RTX 4080"
        filters.min_gpus = count
        filters.max_gpus = count
        title = f"🔵 <b>Топ предложения: RTX 4080 ({count}x GPU)</b>"
    elif category == "cluster":
        filters.min_gpus = count
        filters.max_gpus = count
        title = f"🟣 <b>Топ предложения: Мульти-GPU Кластер ({count}x карт)</b>"
    elif category == "budget":
        filters.max_dph = 0.35
        filters.min_gpus = 1
        title = "💰 <b>Топ предложения: Бюджетные GPU (< $0.35/час)</b>"

    await call.message.edit_text("🔍 <i>Поиск лучших серверов на Vast.ai... Пожалуйста, подождите...</i>", parse_mode="HTML")
    await call.answer()

    try:
        offers = await vast_client.search_offers(filters, limit=5)
    except Exception as e:
        logger.error("Error searching template offers: %s", e)
        await call.message.edit_text(
            f"❌ <b>Ошибка при поиске:</b>\n<code>{e}</code>",
            parse_mode="HTML",
            reply_markup=get_templates_menu_kb(),
        )
        return

    if not offers:
        await call.message.edit_text(
            f"{title}\n\n"
            "😔 В данный момент нет свободных предложений, подходящих под этот шаблон.\n"
            "Попробуйте выбрать другой шаблон или воспользоваться гибким поиском.",
            parse_mode="HTML",
            reply_markup=get_templates_menu_kb(),
        )
        return

    cards = [format_offer_card(offer, rank=i) for i, offer in enumerate(offers, 1)]
    result_text = f"{title}\n\n" + "\n\n─────────────────\n\n".join(cards) + "\n\n👇 Выберите сервер для перехода к настройке и аренде:"

    kb = get_offers_list_kb(offers, prefix="rent_offer")
    await call.message.edit_text(result_text, parse_mode="HTML", reply_markup=kb)

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from ..keyboards.common_kb import get_main_menu_kb, get_back_to_main_kb
from ..api.vast_client import VastApiClient

router = Router()

START_TEXT = (
    "🤖 <b>Панель управления Vast.ai GPU</b>\n\n"
    "С помощью этого бота вы можете:\n"
    "• 🖥 Управлять серверами (просмотр, SSH, старт, стоп)\n"
    "• 💥 <b>Мгновенно уничтожать (KILL)</b> зависшие серверы прямо во время загрузки Docker\n"
    "• ⚡ Арендовать <b>RTX 4090 / 4080</b> (1x, 4x, 8x GPU) в 1 клик\n"
    "• 🔍 Искать любые GPU по лучшим ценам\n"
    "• 💳 Контролировать баланс и почасовой расход\n\n"
    "Выберите нужное действие в меню ниже 👇"
)

HELP_TEXT = (
    "❓ <b>Справка по работе с ботом Vast.ai</b>\n\n"
    "• <b>Мои серверы</b>: список активных и остановленных машин. Отображает статус скачивания докера, готовность SSH и открытые порты.\n\n"
    "• <b>Кнопка KILL</b>: принудительно удаляет сервер через API Vast.ai даже в процессе загрузки Docker-образа (статус <code>loading</code> / <code>downloading</code>), чтобы не тратить баланс на медленный или сбойный хост.\n\n"
    "• <b>Быстрые шаблоны</b>: готовые фильтры для моментального поиска самых дешевых и надежных нод с RTX 4090, RTX 4080 и мульти-GPU кластеров.\n\n"
    "• <b>Команды бота:</b>\n"
    "/start — Главное меню\n"
    "/servers — Мои серверы\n"
    "/templates — Шаблоны RTX 4090 / 4080\n"
    "/balance — Баланс и расходы\n"
    "/help — Эта справка"
)


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(START_TEXT, parse_mode="HTML", reply_markup=get_main_menu_kb())


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(HELP_TEXT, parse_mode="HTML", reply_markup=get_back_to_main_kb())


@router.callback_query(F.data == "menu:main")
async def cb_main_menu(call: CallbackQuery):
    await call.message.edit_text(START_TEXT, parse_mode="HTML", reply_markup=get_main_menu_kb())
    await call.answer()


@router.callback_query(F.data == "menu:help")
async def cb_help(call: CallbackQuery):
    await call.message.edit_text(HELP_TEXT, parse_mode="HTML", reply_markup=get_back_to_main_kb())
    await call.answer()

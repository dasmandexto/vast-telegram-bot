from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu_kb() -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(text="🖥 Мои серверы", callback_data="menu:instances"),
        ],
        [
            InlineKeyboardButton(text="⚡ Быстрые шаблоны GPU", callback_data="menu:templates"),
        ],
        [
            InlineKeyboardButton(text="🔍 Поиск и аренда GPU", callback_data="menu:search"),
            InlineKeyboardButton(text="💳 Баланс", callback_data="menu:account"),
        ],
        [
            InlineKeyboardButton(text="❓ Помощь", callback_data="menu:help"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_back_to_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🔙 Главное меню", callback_data="menu:main")]]
    )

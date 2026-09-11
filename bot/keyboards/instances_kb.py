from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from ..api.models import Instance


def get_instances_list_kb(instances: List[Instance]) -> InlineKeyboardMarkup:
    rows = []
    for inst in instances:
        if inst.is_loading:
            icon = "🟡 [Loading]"
        elif inst.is_running:
            icon = "🟢 [Run]"
        elif inst.is_stopped:
            icon = "⏸️ [Stop]"
        else:
            icon = "🔴 [Off]"

        label = f"{icon} #{inst.id} ({inst.num_gpus}x {inst.gpu_name})"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"inst:view:{inst.id}")])

    rows.append([
        InlineKeyboardButton(text="🔄 Обновить список", callback_data="inst:refresh_list"),
        InlineKeyboardButton(text="🔙 Главное меню", callback_data="menu:main"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_instance_actions_kb(instance: Instance) -> InlineKeyboardMarkup:
    rows = []

    # Row 1: Refresh + Start/Stop
    action_row = [InlineKeyboardButton(text="🔄 Обновить", callback_data=f"inst:view:{instance.id}")]
    if instance.is_running or instance.is_loading:
        action_row.append(InlineKeyboardButton(text="🛑 Остановить", callback_data=f"inst:confirm_stop:{instance.id}"))
    elif instance.is_stopped:
        action_row.append(InlineKeyboardButton(text="⚡ Запустить", callback_data=f"inst:start:{instance.id}"))
    rows.append(action_row)

    # Row 2: Reboot (if running) + Direct KILL (Red button)
    row2 = []
    if instance.is_running:
        row2.append(InlineKeyboardButton(text="🔄 Перезагрузить", callback_data=f"inst:reboot:{instance.id}"))

    # KILL button is ALWAYS highlighted and available, especially when loading docker
    row2.append(InlineKeyboardButton(text="💥 УБИТЬ (KILL)", callback_data=f"inst:confirm_kill:{instance.id}"))
    rows.append(row2)

    # Row 3: Back buttons
    rows.append([
        InlineKeyboardButton(text="🔙 К списку серверов", callback_data="menu:instances"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu:main"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_confirm_kill_kb(instance_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🚨 ДА, УНИЧТОЖИТЬ СЕРВЕР 🚨", callback_data=f"inst:kill:{instance_id}"),
            ],
            [
                InlineKeyboardButton(text="❌ Отмена", callback_data=f"inst:view:{instance_id}"),
            ],
        ]
    )


def get_confirm_stop_kb(instance_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🛑 Да, остановить", callback_data=f"inst:stop:{instance_id}"),
            ],
            [
                InlineKeyboardButton(text="❌ Отмена", callback_data=f"inst:view:{instance_id}"),
            ],
        ]
    )

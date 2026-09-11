import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from ..api.vast_client import VastApiClient, VastApiError
from ..utils.formatters import format_instance_card
from ..keyboards.instances_kb import (
    get_instances_list_kb,
    get_instance_actions_kb,
    get_confirm_kill_kb,
    get_confirm_stop_kb,
)
from ..keyboards.common_kb import get_back_to_main_kb

logger = logging.getLogger(__name__)
router = Router()


async def show_instances_list(target: Message | CallbackQuery, vast_client: VastApiClient):
    try:
        instances = await vast_client.get_instances()
    except Exception as e:
        logger.error("Error fetching instances: %s", e)
        error_msg = f"❌ <b>Ошибка получения списка серверов:</b>\n<code>{e}</code>"
        if isinstance(target, CallbackQuery):
            await target.message.edit_text(error_msg, parse_mode="HTML", reply_markup=get_back_to_main_kb())
            await target.answer()
        else:
            await target.answer(error_msg, parse_mode="HTML", reply_markup=get_back_to_main_kb())
        return

    if not instances:
        text = (
            "🖥 <b>У вас пока нет активных серверов на Vast.ai</b>\n\n"
            "Вы можете быстро арендовать сервер в разделе <b>⚡ Быстрые шаблоны GPU</b> или через <b>🔍 Поиск</b>."
        )
        if isinstance(target, CallbackQuery):
            await target.message.edit_text(text, parse_mode="HTML", reply_markup=get_back_to_main_kb())
            await target.answer()
        else:
            await target.answer(text, parse_mode="HTML", reply_markup=get_back_to_main_kb())
        return

    # Count statuses
    running_cnt = sum(1 for i in instances if i.is_running)
    loading_cnt = sum(1 for i in instances if i.is_loading)
    stopped_cnt = sum(1 for i in instances if i.is_stopped)

    header = (
        f"🖥 <b>Ваши серверы Vast.ai ({len(instances)} шт.):</b>\n"
        f"🟢 Работают: {running_cnt} | 🟡 Загружаются: {loading_cnt} | ⏸️ Остановлены: {stopped_cnt}\n\n"
        f"Выберите сервер для просмотра данных, SSH или управления (Kill / Stop / Reboot):"
    )

    kb = get_instances_list_kb(instances)
    if isinstance(target, CallbackQuery):
        await target.message.edit_text(header, parse_mode="HTML", reply_markup=kb)
        await target.answer()
    else:
        await target.answer(header, parse_mode="HTML", reply_markup=kb)


@router.message(Command("servers"))
async def cmd_servers(message: Message, vast_client: VastApiClient):
    await show_instances_list(message, vast_client)


@router.callback_query(F.data == "menu:instances")
async def cb_instances_menu(call: CallbackQuery, vast_client: VastApiClient):
    await show_instances_list(call, vast_client)


@router.callback_query(F.data == "inst:refresh_list")
async def cb_refresh_list(call: CallbackQuery, vast_client: VastApiClient):
    await show_instances_list(call, vast_client)


@router.callback_query(F.data.startswith("inst:view:"))
async def cb_view_instance(call: CallbackQuery, vast_client: VastApiClient):
    instance_id = int(call.data.split(":")[2])
    try:
        instance = await vast_client.get_instance(instance_id)
    except Exception as e:
        await call.answer(f"Ошибка загрузки: {e}", show_alert=True)
        return

    if not instance:
        await call.answer("Сервер не найден или уже был удален!", show_alert=True)
        await show_instances_list(call, vast_client)
        return

    text = format_instance_card(instance)
    kb = get_instance_actions_kb(instance)
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    await call.answer()


@router.callback_query(F.data.startswith("inst:start:"))
async def cb_start_instance(call: CallbackQuery, vast_client: VastApiClient):
    instance_id = int(call.data.split(":")[2])
    await call.answer("⚡ Запускаем сервер...")
    try:
        await vast_client.start_instance(instance_id)
        instance = await vast_client.get_instance(instance_id)
        if instance:
            await call.message.edit_text(
                f"✅ Команда на запуск отправлена!\n\n" + format_instance_card(instance),
                parse_mode="HTML",
                reply_markup=get_instance_actions_kb(instance),
            )
        else:
            await show_instances_list(call, vast_client)
    except Exception as e:
        await call.answer(f"Ошибка запуска: {e}", show_alert=True)


@router.callback_query(F.data.startswith("inst:confirm_stop:"))
async def cb_confirm_stop(call: CallbackQuery):
    instance_id = int(call.data.split(":")[2])
    text = (
        f"🛑 <b>Подтверждение остановки сервера #{instance_id}</b>\n\n"
        "При остановке сервера:\n"
        "• Диск и установленные файлы сохраняются\n"
        "• Оплата за GPU прекращается (списывается только небольшая плата за хранение диска)\n"
        "• SSH подключение прерывается\n\n"
        "Вы действительно хотите остановить сервер?"
    )
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_confirm_stop_kb(instance_id))
    await call.answer()


@router.callback_query(F.data.startswith("inst:stop:"))
async def cb_stop_instance(call: CallbackQuery, vast_client: VastApiClient):
    instance_id = int(call.data.split(":")[2])
    await call.answer("🛑 Останавливаем сервер...")
    try:
        await vast_client.stop_instance(instance_id)
        instance = await vast_client.get_instance(instance_id)
        if instance:
            await call.message.edit_text(
                f"✅ Сервер останавливается.\n\n" + format_instance_card(instance),
                parse_mode="HTML",
                reply_markup=get_instance_actions_kb(instance),
            )
        else:
            await show_instances_list(call, vast_client)
    except Exception as e:
        await call.answer(f"Ошибка остановки: {e}", show_alert=True)


@router.callback_query(F.data.startswith("inst:reboot:"))
async def cb_reboot_instance(call: CallbackQuery, vast_client: VastApiClient):
    instance_id = int(call.data.split(":")[2])
    await call.answer("🔄 Перезагружаем...")
    try:
        await vast_client.reboot_instance(instance_id)
        await call.answer("✅ Сервер отправлен на перезагрузку!", show_alert=True)
        instance = await vast_client.get_instance(instance_id)
        if instance:
            await call.message.edit_text(format_instance_card(instance), parse_mode="HTML", reply_markup=get_instance_actions_kb(instance))
    except Exception as e:
        await call.answer(f"Ошибка перезагрузки: {e}", show_alert=True)


@router.callback_query(F.data.startswith("inst:confirm_kill:"))
async def cb_confirm_kill(call: CallbackQuery):
    instance_id = int(call.data.split(":")[2])
    text = (
        f"🚨 <b>ВНИМАНИЕ: УНИЧТОЖЕНИЕ СЕРВЕРА #{instance_id} (KILL)</b> 🚨\n\n"
        "• Все данные на диске будут <b>безвозвратно удалены</b>\n"
        "• Аренда немедленно завершится, списания баланса прекратятся\n"
        "• Если сервер прямо сейчас завис на скачивании Docker (<code>loading</code>), он будет немедленно убит!\n\n"
        "Подтвердить уничтожение сервера?"
    )
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_confirm_kill_kb(instance_id))
    await call.answer()


@router.callback_query(F.data.startswith("inst:kill:"))
async def cb_kill_instance(call: CallbackQuery, vast_client: VastApiClient):
    instance_id = int(call.data.split(":")[2])
    await call.answer("💥 Уничтожаем сервер...")
    try:
        await vast_client.destroy_instance(instance_id)
        await call.message.edit_text(
            f"💥 <b>Сервер #{instance_id} успешно уничтожен (KILL)!</b>\n\n"
            f"Списания прекращены, ресурсы освобождены.",
            parse_mode="HTML",
            reply_markup=get_back_to_main_kb(),
        )
    except Exception as e:
        logger.error("Failed to kill instance %s: %s", instance_id, e)
        await call.answer(f"Ошибка при уничтожении: {e}", show_alert=True)

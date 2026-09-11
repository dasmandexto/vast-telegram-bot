import logging
from typing import Optional
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from ..api.vast_client import VastApiClient
from ..api.models import SearchFilters
from ..utils.formatters import format_offer_card
from ..keyboards.search_kb import (
    get_gpu_models_kb,
    get_gpu_counts_kb,
    get_docker_presets_kb,
    get_disk_size_kb,
    get_offers_list_kb,
    get_confirm_rent_kb,
)
from ..keyboards.common_kb import get_back_to_main_kb

logger = logging.getLogger(__name__)
router = Router()


class SearchWizard(StatesGroup):
    waiting_for_model = State()
    waiting_for_count = State()
    waiting_for_custom_img = State()
    waiting_for_custom_disk = State()


@router.callback_query(F.data == "menu:search")
async def cb_start_search(call: CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        "🔍 <b>Поиск и аренда GPU на Vast.ai</b>\n\n"
        "<b>Шаг 1 из 2:</b> Выберите интересующую модель видеокарты:"
    )
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_gpu_models_kb())
    await call.answer()


@router.callback_query(F.data.startswith("search_gpu:"))
async def cb_select_gpu(call: CallbackQuery, state: FSMContext):
    gpu_model = call.data.split(":")[1]
    await state.update_data(gpu_model=None if gpu_model == "any" else gpu_model)

    text = (
        f"🔍 Выбранная модель: <b>{gpu_model.upper()}</b>\n\n"
        "<b>Шаг 2 из 2:</b> Выберите необходимое количество видеокарт в одной ноде:"
    )
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_gpu_counts_kb())
    await call.answer()


@router.callback_query(F.data.startswith("search_count:"))
async def cb_select_count(call: CallbackQuery, state: FSMContext, vast_client: VastApiClient):
    count_str = call.data.split(":")[1]
    data = await state.get_data()
    gpu_model = data.get("gpu_model")

    filters = SearchFilters()
    if gpu_model:
        filters.gpu_name = gpu_model

    if count_str != "any":
        count = int(count_str)
        filters.min_gpus = count
        filters.max_gpus = count

    await call.message.edit_text("🔍 <i>Поиск доступных GPU предложений... Пожалуйста, подождите...</i>", parse_mode="HTML")
    await call.answer()

    try:
        offers = await vast_client.search_offers(filters, limit=6)
    except Exception as e:
        logger.error("Search error: %s", e)
        await call.message.edit_text(f"❌ <b>Ошибка поиска:</b>\n<code>{e}</code>", parse_mode="HTML", reply_markup=get_back_to_main_kb())
        return

    if not offers:
        await call.message.edit_text(
            "😔 По вашему запросу не найдено подходящих серверов.\n"
            "Попробуйте изменить параметры поиска или выбрать другую модель.",
            parse_mode="HTML",
            reply_markup=get_back_to_main_kb(),
        )
        return

    cards = [format_offer_card(offer, rank=i) for i, offer in enumerate(offers, 1)]
    result_text = "🎯 <b>Найденные варианты на Vast.ai:</b>\n\n" + "\n\n─────────────────\n\n".join(cards) + "\n\n👇 Выберите сервер для аренды:"

    await call.message.edit_text(result_text, parse_mode="HTML", reply_markup=get_offers_list_kb(offers))


# --- Rental Flow: Step 1 Select Image ---
@router.callback_query(F.data.startswith("rent_offer:"))
async def cb_select_offer_for_rent(call: CallbackQuery, state: FSMContext):
    offer_id = int(call.data.split(":")[1])
    await state.update_data(offer_id=offer_id)

    text = (
        f"⚙️ <b>Настройка сервера (Оффер #{offer_id})</b>\n\n"
        "<b>Шаг 1:</b> Выберите базовый Docker-образ или введите свой:"
    )
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_docker_presets_kb(offer_id))
    await call.answer()


@router.callback_query(F.data.startswith("rent_img:"))
async def cb_selected_docker_image(call: CallbackQuery, state: FSMContext):
    parts = call.data.split(":")
    offer_id = int(parts[1])
    image = ":".join(parts[2:])

    await state.update_data(image=image)
    text = (
        f"⚙️ <b>Настройка сервера (Оффер #{offer_id})</b>\n"
        f"Образ: <code>{image}</code>\n\n"
        "<b>Шаг 2:</b> Выберите размер SSD диска (GB):"
    )
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_disk_size_kb(offer_id, image))
    await call.answer()


@router.callback_query(F.data.startswith("rent_custom_img:"))
async def cb_prompt_custom_image(call: CallbackQuery, state: FSMContext):
    offer_id = int(call.data.split(":")[1])
    await state.update_data(offer_id=offer_id)
    await state.set_state(SearchWizard.waiting_for_custom_img)

    await call.message.edit_text(
        f"✏️ <b>Введите имя Docker-образа</b> для оффера #{offer_id}\n\n"
        "Например: <code>pytorch/pytorch:2.1.2-cuda12.1-cudnn8-devel</code>\n"
        "Отправьте сообщение с названием образа:",
        parse_mode="HTML",
    )
    await call.answer()


@router.message(SearchWizard.waiting_for_custom_img)
async def msg_custom_image_entered(message: Message, state: FSMContext):
    image = message.text.strip()
    data = await state.get_data()
    offer_id = data.get("offer_id")

    await state.update_data(image=image)
    await state.set_state(None)

    text = (
        f"⚙️ <b>Настройка сервера (Оффер #{offer_id})</b>\n"
        f"Образ: <code>{image}</code>\n\n"
        "<b>Шаг 2:</b> Выберите размер SSD диска (GB):"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=get_disk_size_kb(offer_id, image))


# --- Rental Flow: Step 2 Select Disk Size ---
@router.callback_query(F.data.startswith("rent_disk:"))
async def cb_selected_disk_size(call: CallbackQuery, state: FSMContext):
    parts = call.data.split(":")
    offer_id = int(parts[1])
    disk_gb = float(parts[2])

    data = await state.get_data()
    image = data.get("image", "pytorch/pytorch:latest")
    await state.update_data(disk_gb=disk_gb)

    text = (
        f"🚀 <b>Подтверждение аренды сервера Vast.ai</b>\n\n"
        f"🆔 Оффер ID: <code>{offer_id}</code>\n"
        f"📦 Docker-образ: <code>{image}</code>\n"
        f"💾 Размер диска: <b>{disk_gb:.0f} GB</b>\n\n"
        f"<i>После подтверждения нода будет зарезервирована, и хост начнет скачивание Docker-образа. "
        f"Вы сможете отслеживать статус и в любой момент принудительно остановить или уничтожить (KILL) инстанс в разделе «Мои серверы».</i>"
    )
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_confirm_rent_kb(offer_id))
    await call.answer()


@router.callback_query(F.data.startswith("rent_custom_disk:"))
async def cb_prompt_custom_disk(call: CallbackQuery, state: FSMContext):
    offer_id = int(call.data.split(":")[1])
    await state.update_data(offer_id=offer_id)
    await state.set_state(SearchWizard.waiting_for_custom_disk)

    await call.message.edit_text(
        f"✏️ <b>Введите размер диска в GB (число):</b>\n\n"
        "Например: <code>80</code>\n"
        "Отправьте сообщение с размером:",
        parse_mode="HTML",
    )
    await call.answer()


@router.message(SearchWizard.waiting_for_custom_disk)
async def msg_custom_disk_entered(message: Message, state: FSMContext):
    try:
        disk_gb = float(message.text.strip())
        if disk_gb < 10 or disk_gb > 2000:
            await message.answer("⚠️ Введите корректный размер диска от 10 до 2000 GB:")
            return
    except ValueError:
        await message.answer("⚠️ Пожалуйста, введите число (например: 60):")
        return

    data = await state.get_data()
    offer_id = data.get("offer_id")
    image = data.get("image", "pytorch/pytorch:latest")
    await state.update_data(disk_gb=disk_gb)
    await state.set_state(None)

    text = (
        f"🚀 <b>Подтверждение аренды сервера Vast.ai</b>\n\n"
        f"🆔 Оффер ID: <code>{offer_id}</code>\n"
        f"📦 Docker-образ: <code>{image}</code>\n"
        f"💾 Размер диска: <b>{disk_gb:.0f} GB</b>\n\n"
        f"Подтвердить запуск инстанса?"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=get_confirm_rent_kb(offer_id))


# --- Rental Flow: Step 3 Execute Order ---
@router.callback_query(F.data.startswith("rent_confirm:"))
async def cb_execute_rent(call: CallbackQuery, state: FSMContext, vast_client: VastApiClient):
    offer_id = int(call.data.split(":")[1])
    data = await state.get_data()
    image = data.get("image", "pytorch/pytorch:latest")
    disk_gb = float(data.get("disk_gb", 30.0))

    await call.message.edit_text("⏳ <i>Отправка команды аренды в Vast.ai API...</i>", parse_mode="HTML")
    await call.answer()

    try:
        res = await vast_client.create_instance(offer_id=offer_id, image=image, disk_space=disk_gb)
        new_id = res.get("new_contract") or res.get("id") or "создан"

        await state.clear()
        text = (
            f"🎉 <b>Сервер успешно арендован!</b>\n\n"
            f"🆔 Номер контракта/сервера: <code>{new_id}</code>\n"
            f"📦 Образ: <code>{image}</code>\n"
            f"💾 Диск: <b>{disk_gb:.0f} GB</b>\n\n"
            f"Хост начал подготовку и скачивание контейнера.\n"
            f"Вы можете проверить статус загрузки и подключиться в меню <b>🖥 Мои серверы</b>."
        )
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=get_back_to_main_kb())
    except Exception as e:
        logger.error("Failed to rent instance: %s", e)
        await call.message.edit_text(
            f"❌ <b>Ошибка при создании инстанса:</b>\n<code>{e}</code>\n\n"
            "Возможно, предложение уже занято другим пользователем или недостаточно средств на балансе.",
            parse_mode="HTML",
            reply_markup=get_back_to_main_kb(),
        )

from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from ..api.models import Offer


def get_templates_menu_kb() -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(text="🟢 RTX 4090 (1x 24GB)", callback_data="tmpl:rtx4090:1"),
            InlineKeyboardButton(text="🟢 RTX 4090 (4x 96GB)", callback_data="tmpl:rtx4090:4"),
        ],
        [
            InlineKeyboardButton(text="🟢 RTX 4090 (8x 192GB)", callback_data="tmpl:rtx4090:8"),
            InlineKeyboardButton(text="🔵 RTX 4080 (1x 16GB)", callback_data="tmpl:rtx4080:1"),
        ],
        [
            InlineKeyboardButton(text="🔵 RTX 4080 (4x 64GB)", callback_data="tmpl:rtx4080:4"),
            InlineKeyboardButton(text="🔵 RTX 4080 (8x 128GB)", callback_data="tmpl:rtx4080:8"),
        ],
        [
            InlineKeyboardButton(text="🟣 Кластер 4x GPU (любой)", callback_data="tmpl:cluster:4"),
            InlineKeyboardButton(text="🟣 Кластер 8x GPU (любой)", callback_data="tmpl:cluster:8"),
        ],
        [
            InlineKeyboardButton(text="💰 Бюджетный GPU (< $0.35/ч)", callback_data="tmpl:budget:1"),
        ],
        [
            InlineKeyboardButton(text="🔙 Главное меню", callback_data="menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_gpu_models_kb() -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(text="RTX 4090", callback_data="search_gpu:RTX 4090"),
            InlineKeyboardButton(text="RTX 4080", callback_data="search_gpu:RTX 4080"),
        ],
        [
            InlineKeyboardButton(text="RTX 3090", callback_data="search_gpu:RTX 3090"),
            InlineKeyboardButton(text="RTX 3080", callback_data="search_gpu:RTX 3080"),
        ],
        [
            InlineKeyboardButton(text="A100 (SXM4/PCIe)", callback_data="search_gpu:A100"),
            InlineKeyboardButton(text="H100 (PCIe/SXM)", callback_data="search_gpu:H100"),
        ],
        [
            InlineKeyboardButton(text="Любая видеокарта (Any)", callback_data="search_gpu:any"),
        ],
        [
            InlineKeyboardButton(text="🔙 Главное меню", callback_data="menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_gpu_counts_kb() -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(text="1x GPU", callback_data="search_count:1"),
            InlineKeyboardButton(text="2x GPU", callback_data="search_count:2"),
        ],
        [
            InlineKeyboardButton(text="4x GPU", callback_data="search_count:4"),
            InlineKeyboardButton(text="8x GPU", callback_data="search_count:8"),
        ],
        [
            InlineKeyboardButton(text="Любое кол-во (1+)", callback_data="search_count:any"),
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="menu:search"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_docker_presets_kb(offer_id: int) -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(text="🔥 PyTorch (latest)", callback_data=f"rent_img:{offer_id}:pytorch/pytorch:latest"),
        ],
        [
            InlineKeyboardButton(text="⚡ CUDA 12.2 + Ubuntu 22.04", callback_data=f"rent_img:{offer_id}:nvidia/cuda:12.2.0-devel-ubuntu22.04"),
        ],
        [
            InlineKeyboardButton(text="🦙 Ollama LLM", callback_data=f"rent_img:{offer_id}:ollama/ollama:latest"),
            InlineKeyboardButton(text="🚀 vLLM OpenAI Server", callback_data=f"rent_img:{offer_id}:vllm/vllm-openai:latest"),
        ],
        [
            InlineKeyboardButton(text="🎨 Stable Diffusion WebUI", callback_data=f"rent_img:{offer_id}:runpod/stable-diffusion:webui-1.8.0"),
        ],
        [
            InlineKeyboardButton(text="✏️ Ввести свой Docker Image", callback_data=f"rent_custom_img:{offer_id}"),
        ],
        [
            InlineKeyboardButton(text="❌ Отмена", callback_data="menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_disk_size_kb(offer_id: int, image_name: str) -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(text="💾 30 GB", callback_data=f"rent_disk:{offer_id}:30"),
            InlineKeyboardButton(text="💾 50 GB", callback_data=f"rent_disk:{offer_id}:50"),
        ],
        [
            InlineKeyboardButton(text="💾 100 GB", callback_data=f"rent_disk:{offer_id}:100"),
            InlineKeyboardButton(text="💾 200 GB", callback_data=f"rent_disk:{offer_id}:200"),
        ],
        [
            InlineKeyboardButton(text="✏️ Ввести свой объем (GB)", callback_data=f"rent_custom_disk:{offer_id}"),
        ],
        [
            InlineKeyboardButton(text="❌ Отмена", callback_data="menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_offers_list_kb(offers: List[Offer], prefix: str = "rent_offer") -> InlineKeyboardMarkup:
    rows = []
    for i, offer in enumerate(offers, 1):
        price = f"${offer.dph_total:.2f}/ч"
        label = f"🚀 Арендовать #{i} ({offer.num_gpus}x {offer.gpu_name} - {price})"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"{prefix}:{offer.id}")])

    rows.append([
        InlineKeyboardButton(text="🔄 Повторить поиск", callback_data="menu:search"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu:main"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_confirm_rent_kb(offer_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ ПОДТВЕРДИТЬ АРЕНДУ", callback_data=f"rent_confirm:{offer_id}"),
            ],
            [
                InlineKeyboardButton(text="❌ Отмена", callback_data="menu:main"),
            ],
        ]
    )

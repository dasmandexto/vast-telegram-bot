import html
from typing import Optional
from ..api.models import Instance, Offer, UserInfo


def format_status_badge(instance: Instance) -> str:
    status = (instance.actual_status or "").lower()
    msg = (instance.status_msg or "").lower()

    if instance.is_loading:
        return "🟡 <b>Загрузка Docker...</b>"
    elif status == "running":
        return "🟢 <b>Работает</b>"
    elif status in ["stopped", "inactive"]:
        return "⏸️ <b>Остановлен</b>"
    elif status == "offline":
        return "🔴 <b>Офлайн</b>"
    else:
        return f"⚪ <b>{html.escape(instance.actual_status)}</b>"


def format_instance_card(instance: Instance) -> str:
    status_badge = format_status_badge(instance)
    gpu_label = f"{instance.num_gpus}x {html.escape(instance.gpu_name)}"
    price = f"${instance.dph_total:.3f}/час"

    lines = [
        f"🖥 <b>Сервер #{instance.id}</b>",
        f"Статус: {status_badge}",
        f"Графика: <b>{gpu_label}</b>",
        f"Стоимость: <b>{price}</b>",
    ]

    if instance.disk_space:
        lines.append(f"Диск: <b>{instance.disk_space:.0f} GB</b>")

    if instance.image_uuid:
        lines.append(f"Образ: <code>{html.escape(instance.image_uuid)}</code>")

    # Display docker pull progress or host status message if present
    if instance.status_msg:
        clean_msg = html.escape(instance.status_msg.strip())
        lines.append(f"Инфо: <i>{clean_msg}</i>")

    # SSH Connection Details
    if instance.is_running and instance.ssh_host and instance.ssh_port:
        lines.append("")
        lines.append("🔑 <b>SSH подключение:</b>")
        lines.append(f"<code>{instance.ssh_command}</code>")

        if instance.direct_port_start and instance.direct_port_end:
            lines.append(f"🌐 <b>Прямые порты:</b> <code>{instance.direct_port_start}-{instance.direct_port_end}</code>")
    elif instance.is_loading:
        lines.append("")
        lines.append("⏳ <i>Идет загрузка Docker-образа на хост... Можно остановить или уничтожить (KILL), если хост завис.</i>")

    return "\n".join(lines)


def format_offer_card(offer: Offer, rank: Optional[int] = None) -> str:
    prefix = f"<b>#{rank}</b> " if rank else ""
    gpu_label = f"{offer.num_gpus}x {html.escape(offer.gpu_name)}"
    price = f"<b>${offer.dph_total:.3f}/час</b>"
    vram = offer.formatted_gpu_ram_gb
    reliability = offer.reliability_percent
    
    speed_down = f"{offer.inet_down:.0f} Mbps" if offer.inet_down else "N/A"
    cpu = f"{offer.cpu_cores} vCPU, {offer.formatted_cpu_ram_gb} RAM" if offer.cpu_cores else "N/A"
    cuda = f"CUDA {offer.cuda_max_good:.1f}" if offer.cuda_max_good else "N/A"
    verified = " ✅ Verified" if offer.verified else ""

    lines = [
        f"{prefix}🚀 <b>{gpu_label}</b> ({vram}){verified}",
        f"💰 Цена: {price}",
        f"📊 Надежность хоста: <b>{reliability}</b>",
        f"🌐 Скорость сети: <b>{speed_down}</b>",
        f"⚙️ Система: {cpu} | {cuda}",
        f"🆔 ID оффера: <code>{offer.id}</code>",
    ]
    return "\n".join(lines)


def format_account_card(user_info: UserInfo, total_burn_rate: float = 0.0) -> str:
    balance = user_info.balance
    credit = user_info.credit
    effective_balance = balance + credit

    lines = [
        "💳 <b>Информация об аккаунте Vast.ai</b>",
        "",
        f"💰 Баланс: <b>${balance:.2f}</b>",
    ]
    if credit > 0:
        lines.append(f"🎁 Кредит / Бонусы: <b>${credit:.2f}</b>")
        lines.append(f"💵 Доступно всего: <b>${effective_balance:.2f}</b>")

    if user_info.email:
        lines.append(f"📧 Email: <code>{html.escape(user_info.email)}</code>")

    lines.append("")
    lines.append(f"🔥 Текущий расход: <b>${total_burn_rate:.3f}/час</b>")
    if total_burn_rate > 0:
        burn_day = total_burn_rate * 24
        burn_month = total_burn_rate * 24 * 30
        lines.append(f"📅 Расход в день: ~<b>${burn_day:.2f}</b> | в месяц: ~<b>${burn_month:.2f}</b>")
        
        hours_left = effective_balance / total_burn_rate if total_burn_rate > 0 else 0
        if hours_left >= 24:
            days = int(hours_left // 24)
            rem_hours = int(hours_left % 24)
            lines.append(f"⏳ Баланса хватит примерно на: <b>{days} дн. {rem_hours} ч.</b>")
        else:
            lines.append(f"⏳ Баланса хватит примерно на: <b>{hours_left:.1f} ч.</b>")

    return "\n".join(lines)

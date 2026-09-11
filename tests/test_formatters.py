import pytest
from bot.api.models import Instance, Offer, UserInfo
from bot.utils.formatters import (
    format_status_badge,
    format_instance_card,
    format_offer_card,
    format_account_card,
)


def test_status_badge_loading():
    inst = Instance(
        id=123,
        actual_status="loading",
        status_msg="Pulling docker image pytorch/pytorch:latest 45%",
    )
    badge = format_status_badge(inst)
    assert "Загрузка Docker" in badge
    assert inst.is_loading is True


def test_status_badge_running():
    inst = Instance(
        id=123,
        actual_status="running",
        ssh_host="ssh1.vast.ai",
        ssh_port=2222,
    )
    badge = format_status_badge(inst)
    assert "Работает" in badge
    assert inst.is_running is True
    assert inst.is_loading is False


def test_instance_card_ssh_and_kill():
    inst = Instance(
        id=999,
        actual_status="running",
        gpu_name="RTX 4090",
        num_gpus=1,
        dph_total=0.45,
        ssh_host="ssh5.vast.ai",
        ssh_port=30420,
        direct_port_start=8080,
        direct_port_end=8085,
    )
    card = format_instance_card(inst)
    assert "#999" in card
    assert "1x RTX 4090" in card
    assert "$0.450/час" in card
    assert "ssh -p 30420 root@ssh5.vast.ai -L 8080:localhost:8080" in card
    assert "8080-8085" in card


def test_instance_card_loading_docker():
    inst = Instance(
        id=888,
        actual_status="loading",
        gpu_name="RTX 4080",
        num_gpus=4,
        dph_total=1.20,
        status_msg="Downloading image layers (62%)",
    )
    card = format_instance_card(inst)
    assert "Загрузка Docker" in card
    assert "Downloading image layers (62%)" in card
    assert "Идет загрузка Docker-образа" in card


def test_offer_card_formatting():
    offer = Offer(
        id=5555,
        gpu_name="RTX 4090",
        num_gpus=1,
        gpu_ram=24576.0,  # 24 GB in MB
        dph_total=0.38,
        reliability2=0.985,
        inet_down=500.0,
        cpu_cores=16,
        cpu_ram=65536.0,
        cuda_max_good=12.2,
        verified=True,
    )
    card = format_offer_card(offer, rank=1)
    assert "1x RTX 4090" in card
    assert "24 GB" in card
    assert "$0.380/час" in card
    assert "98.5%" in card
    assert "500 Mbps" in card
    assert "Verified" in card


def test_account_card():
    user = UserInfo(
        user_id=123,
        email="user@test.com",
        balance=50.0,
        credit=10.0,
    )
    card = format_account_card(user, total_burn_rate=0.50)
    assert "$50.00" in card
    assert "$10.00" in card
    assert "$60.00" in card
    assert "$0.500/час" in card
    assert "user@test.com" in card

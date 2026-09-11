# 🤖 Vast.ai Telegram Bot

Полнофункциональный асинхронный Telegram-бот на **Python** (`aiogram 3.x`, `httpx`, `pydantic-settings`) для управления GPU серверами на платформе **[Vast.ai](https://cloud.vast.ai/)**.

---

## 🌟 Основные возможности

### 1. ⚡ Шаблоны GPU в 1 клик
* 🟢 **RTX 4090**: 1x (24GB), 4x (96GB), 8x (192GB VRAM)
* 🔵 **RTX 4080**: 1x (16GB), 4x (64GB), 8x (128GB VRAM)
* 🟣 **Мульти-GPU Кластеры**: 4x и 8x любых доступных видеокарт
* 💰 **Бюджетный поиск**: видеокарты дешевле `$0.35/час`
* 🔍 **Гибкий поиск**: выбор модели (4090, 4080, 3090, A100, H100), количества карт, фильтрация по надежности хоста (>90%) и цене.

### 2. 🖥 Управление серверами («Мои серверы»)
* **Статусы в реальном времени**:
  * 🟢 **Работает (`running`)** — готов к работе по SSH.
  * 🟡 **Загрузка Docker (`loading` / `downloading`)** — отображает ход скачивания слоев образа и статус хоста.
  * ⏸️ **Остановлен (`stopped`)**
  * 🔴 **Офлайн (`offline`)**
* **Подключение по SSH** в один клик: готовая команда с пробросом портов (`ssh -p PORT root@HOST -L 8080:localhost:8080`).
* **Отображение открытых прямых портов** (Direct Port Range).

### 3. 💥 Мгновенное уничтожение (KILL) во время загрузки Docker
* Возможность **немедленно уничтожить (KILL)** инстанс через API (`DELETE /api/v0/instances/{id}/`), даже если хост завис при скачивании тяжелого Docker-образа. Это предотвращает потерю баланса.
* Действия: **Остановить (Stop)**, **Запустить (Start)**, **Перезагрузить (Reboot)**, **Уничтожить (Kill)**.

### 4. 📦 Готовые шаблоны Docker-образов
* `pytorch/pytorch:latest` — PyTorch
* `nvidia/cuda:12.2.0-devel-ubuntu22.04` — Чистый Ubuntu + CUDA
* `ollama/ollama:latest` — LLM сервер Ollama
* `vllm/vllm-openai:latest` — Высокопроизводительный LLM бэкенд vLLM
* `runpod/stable-diffusion:webui-1.8.0` — Генерация изображений Automatic1111 SD WebUI
* Возможность указать любой свой Docker Image и размер диска (от 10 до 2000 GB).

### 5. 💳 Баланс и аналитика
* Текущий баланс и бонусные кредиты.
* Расчет расхода в реальном времени: $/час, $/день, $/месяц.
* Прогноз оставшегося времени работы до исчерпания средств.

### 6. 🛡 Защита и безопасность
* Встроенный middleware авторизации: доступ к боту разрешен только Telegram ID из списка `ADMIN_IDS`.

---

## 🚀 Быстрый запуск на сервере (1-Click Installer)

На вашем Linux VPS (Ubuntu/Debian) выполните:

```bash
git clone https://github.com/dasmandexto/vast-telegram-bot.git
cd vast-telegram-bot
bash install.sh
```

Скрипт интерактивно запросит:
1. `TELEGRAM_BOT_TOKEN` (от [@BotFather](https://t.me/BotFather))
2. `VAST_API_KEY` (из [Vast.ai API Keys](https://cloud.vast.ai/manage-keys/))
3. `ADMIN_IDS` (ваш Telegram User ID из [@userinfobot](https://t.me/userinfobot))

И автоматически создаст виртуальное окружение, установит зависимости и сгенерирует скрипты запуска.

---

## 🛠 Ручная установка и запуск

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/dasmandexto/vast-telegram-bot.git
   cd vast-telegram-bot
   ```

2. **Создайте `.env` файл:**
   ```bash
   cp .env.example .env
   nano .env
   ```

3. **Создайте виртуальное окружение и установите зависимости:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Запустите бота:**
   ```bash
   python3 -m bot.main
   ```

---

## 🧪 Запуск тестов

```bash
pytest -v
```

---

## 📁 Структура проекта

```
vast-telegram-bot/
├── bot/
│   ├── api/
│   │   ├── models.py       # Pydantic модели данных Vast.ai
│   │   └── vast_client.py   # Асинхронный REST API клиент Vast.ai
│   ├── handlers/
│   │   ├── start.py        # /start, /help и меню
│   │   ├── instances.py    # Серверы, SSH, Stop/Start/Reboot/Kill
│   │   ├── templates.py    # 1-клик шаблоны (4090, 4080, кластеры)
│   │   ├── search_rent.py  # Мастер поиска, выбор Docker и аренда
│   │   └── account.py      # Баланс и почасовой расход
│   ├── keyboards/
│   │   ├── common_kb.py    # Главное меню и навигация
│   │   ├── instances_kb.py # Кнопки серверов и подтверждения Kill
│   │   └── search_kb.py    # Выбор GPU, Docker, диска и аренда
│   ├── middlewares/
│   │   └── auth.py         # Белый список админов (ADMIN_IDS)
│   ├── utils/
│   │   └── formatters.py   # HTML-форматирование карточек
│   ├── config.py           # Конфигурация и валидация .env
│   └── main.py             # Точка входа в бота
├── tests/
│   ├── test_formatters.py  # Тесты форматирования карточек
│   └── test_vast_client.py # Тесты API клиента и роутинга
├── install.sh              # Автоматический скрипт установки
├── requirements.txt        # Зависимости Python
├── .env.example            # Пример файла конфигурации
└── README.md               # Документация проекта
```
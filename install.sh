#!/usr/bin/env bash
# ==============================================================================
#  🤖 VAST.AI TELEGRAM BOT — ALL-IN-ONE INSTALLER & DEPLOYMENT SCRIPT 🤖
# ==============================================================================

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

clear
echo -e "${CYAN}${BOLD}"
echo "  ██╗   ██╗ █████╗ ███████╗████████╗     █████╗ ██╗"
echo "  ██║   ██║██╔══██╗██╔════╝╚══██╔══╝    ██╔══██╗██║"
echo "  ██║   ██║███████║███████╗   ██║       ███████║██║"
echo "  ╚██╗ ██╔╝██╔══██║╚════██║   ██║       ██╔══██║██║"
echo "   ╚████╔╝ ██║  ██║███████║   ██║   ██╗ ██║  ██║██║"
echo "    ╚═══╝  ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝ ╚═╝  ╚═╝╚═╝"
echo -e "${NC}"
echo -e "${YELLOW}${BOLD}  === Vast.ai Telegram GPU Management Bot Installer ===${NC}\n"

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo -e "${BLUE}[*] Рабочая директория:${NC} $PROJECT_DIR"

# 1. Проверка и установка системных пакетов
echo -e "\n${PURPLE}${BOLD}--- Шаг 1: Проверка системных пакетов (Python 3, venv, git) ---${NC}\n"

if command -v apt-get &>/dev/null; then
    echo -e "${CYAN}Обновление пакетов APT и установка зависимостей...${NC}"
    if [ "$EUID" -eq 0 ]; then
        apt-get update -y
        apt-get install -y python3 python3-pip python3-venv git curl
    else
        echo -e "${YELLOW}[!] Требуются права sudo для установки системных пакетов:${NC}"
        sudo apt-get update -y
        sudo apt-get install -y python3 python3-pip python3-venv git curl
    fi
elif command -v yum &>/dev/null; then
    sudo yum install -y python3 python3-pip git curl
fi

# 2. Интерактивная настройка конфигурации (.env)
echo -e "\n${PURPLE}${BOLD}--- Шаг 2: Настройка конфигурации бота (.env) ---${NC}\n"

EXISTING_TOKEN=""
EXISTING_VAST_KEY=""
EXISTING_ADMINS=""

if [ -f "$PROJECT_DIR/.env" ]; then
    echo -e "${YELLOW}[!] Обнаружен существующий файл .env. Загружаем текущие значения...${NC}"
    EXISTING_TOKEN=$(grep -E "^TELEGRAM_BOT_TOKEN=" "$PROJECT_DIR/.env" | cut -d '=' -f2- || true)
    EXISTING_VAST_KEY=$(grep -E "^VAST_API_KEY=" "$PROJECT_DIR/.env" | cut -d '=' -f2- || true)
    EXISTING_ADMINS=$(grep -E "^ADMIN_IDS=" "$PROJECT_DIR/.env" | cut -d '=' -f2- || true)
fi

# 2.1 Telegram Bot Token
while true; do
    if [ -n "$EXISTING_TOKEN" ]; then
        read -rp "$(echo -e "${CYAN}1. Telegram Bot Token [нажмите Enter для сохранения текущего]: ${NC}")" BOT_TOKEN
        BOT_TOKEN=${BOT_TOKEN:-$EXISTING_TOKEN}
    else
        read -rp "$(echo -e "${CYAN}1. Введите Telegram Bot Token (от @BotFather): ${NC}")" BOT_TOKEN
    fi
    BOT_TOKEN=$(echo "$BOT_TOKEN" | tr -d '[:space:]')
    if [ -n "$BOT_TOKEN" ]; then
        break
    else
        echo -e "${RED}Токен бота не может быть пустым!${NC}"
    fi
done

# 2.2 Vast.ai API Key
while true; do
    if [ -n "$EXISTING_VAST_KEY" ]; then
        read -rp "$(echo -e "${CYAN}2. Vast.ai API Key [нажмите Enter для сохранения текущего]: ${NC}")" VAST_API_KEY
        VAST_API_KEY=${VAST_API_KEY:-$EXISTING_VAST_KEY}
    else
        read -rp "$(echo -e "${CYAN}2. Введите Vast.ai API Key (из https://cloud.vast.ai/manage-keys/): ${NC}")" VAST_API_KEY
    fi
    VAST_API_KEY=$(echo "$VAST_API_KEY" | tr -d '[:space:]')
    if [ -n "$VAST_API_KEY" ]; then
        break
    else
        echo -e "${RED}API ключ Vast.ai не может быть пустым!${NC}"
    fi
done

# 2.3 Admin Telegram IDs
while true; do
    if [ -n "$EXISTING_ADMINS" ]; then
        read -rp "$(echo -e "${CYAN}3. Telegram ID администраторов [Enter = ${EXISTING_ADMINS}]: ${NC}")" ADMIN_IDS
        ADMIN_IDS=${ADMIN_IDS:-$EXISTING_ADMINS}
    else
        read -rp "$(echo -e "${CYAN}3. Введите ваш Telegram User ID (из @userinfobot): ${NC}")" ADMIN_IDS
    fi
    ADMIN_IDS=$(echo "$ADMIN_IDS" | tr -d '[:space:]')
    if [ -n "$ADMIN_IDS" ]; then
        break
    else
        echo -e "${RED}Укажите хотя бы один Telegram User ID для доступа к боту!${NC}"
    fi
done

# Сохранение .env
cat > "$PROJECT_DIR/.env" <<EOF
# ==============================================================================
# Vast.ai Telegram Bot Configuration
# ==============================================================================
TELEGRAM_BOT_TOKEN=${BOT_TOKEN}
VAST_API_KEY=${VAST_API_KEY}
ADMIN_IDS=${ADMIN_IDS}
VAST_API_BASE_URL=https://console.vast.ai
LOG_LEVEL=INFO
EOF

chmod 600 "$PROJECT_DIR/.env"
echo -e "${GREEN}[✓] Файл конфигурации .env успешно сохранен.${NC}"

# 3. Настройка виртуального окружения Python
echo -e "\n${PURPLE}${BOLD}--- Шаг 3: Настройка Python venv и установка библиотек ---${NC}\n"

if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo -e "${CYAN}Создание виртуального окружения venv...${NC}"
    python3 -m venv "$PROJECT_DIR/venv"
fi

"$PROJECT_DIR/venv/bin/pip" install --upgrade pip
"$PROJECT_DIR/venv/bin/pip" install -r "$PROJECT_DIR/requirements.txt"

echo -e "${GREEN}[✓] Зависимости Python успешно установлены.${NC}"

# 4. Создание вспомогательных скриптов управления
echo -e "\n${PURPLE}${BOLD}--- Шаг 4: Создание скриптов запуска ---${NC}\n"

# start.sh (Foreground)
cat > "$PROJECT_DIR/start.sh" << 'EOF'
#!/usr/bin/env bash
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"
source venv/bin/activate
exec python3 -m bot.main
EOF
chmod +x "$PROJECT_DIR/start.sh"

# start_background.sh (nohup)
cat > "$PROJECT_DIR/start_background.sh" << 'EOF'
#!/usr/bin/env bash
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"
if pgrep -f "python3 -m bot.main" > /dev/null; then
    echo "⚠️ Бот уже запущен в фоне!"
    exit 0
fi
source venv/bin/activate
nohup python3 -m bot.main > bot.log 2>&1 &
echo "✅ Бот запущен в фоне! PID: $!"
echo "Логи доступны в: tail -f bot.log"
EOF
chmod +x "$PROJECT_DIR/start_background.sh"

# stop.sh
cat > "$PROJECT_DIR/stop.sh" << 'EOF'
#!/usr/bin/env bash
PID=$(pgrep -f "python3 -m bot.main" || true)
if [ -n "$PID" ]; then
    echo "🛑 Остановка бота (PID: $PID)..."
    kill $PID
    sleep 1
    echo "✅ Бот остановлен."
else
    echo "ℹ️ Запущенных процессов бота не найдено."
fi
EOF
chmod +x "$PROJECT_DIR/stop.sh"

# status.sh
cat > "$PROJECT_DIR/status.sh" << 'EOF'
#!/usr/bin/env bash
PID=$(pgrep -f "python3 -m bot.main" || true)
if [ -n "$PID" ]; then
    echo "🟢 Бот активен (PID: $PID)"
else
    echo "🔴 Бот не запущен."
fi
EOF
chmod +x "$PROJECT_DIR/status.sh"

# 5. Опциональная настройка systemd сервиса
echo -e "\n${PURPLE}${BOLD}--- Шаг 5: Настройка службы systemd (автозапуск) ---${NC}\n"
read -rp "$(echo -e "${CYAN}Настроить systemd службу для автозапуска бота при перезагрузке сервера? [y/N]: ${NC}")" SETUP_SERVICE

if [[ "$SETUP_SERVICE" =~ ^[Yy]$ ]]; then
    SERVICE_FILE="/etc/systemd/system/vast-bot.service"
    CURRENT_USER=$(whoami)
    
    SERVICE_CONTENT="[Unit]
Description=Vast.ai Telegram Bot
After=network.target

[Service]
Type=simple
User=${CURRENT_USER}
WorkingDirectory=${PROJECT_DIR}
ExecStart=${PROJECT_DIR}/venv/bin/python3 -m bot.main
Restart=always
RestartSec=5
EnvironmentFile=${PROJECT_DIR}/.env

[Install]
WantedBy=multi-user.target"

    if [ "$EUID" -eq 0 ]; then
        echo "$SERVICE_CONTENT" > "$SERVICE_FILE"
        systemctl daemon-reload
        systemctl enable vast-bot.service
        systemctl restart vast-bot.service
    else
        echo "$SERVICE_CONTENT" | sudo tee "$SERVICE_FILE" > /dev/null
        sudo systemctl daemon-reload
        sudo systemctl enable vast-bot.service
        sudo systemctl restart vast-bot.service
    fi
    echo -e "${GREEN}[✓] Служба vast-bot.service успешно установлена и запущена!${NC}"
    echo -e "${CYAN}Управление службой: sudo systemctl status/restart/stop vast-bot${NC}"
fi

echo -e "\n${GREEN}${BOLD}==============================================================================${NC}"
echo -e "${GREEN}${BOLD}  🎉 УСТАНОВКА УСПЕШНО ЗАВЕРШЕНА! 🎉${NC}"
echo -e "${GREEN}${BOLD}==============================================================================${NC}\n"
echo -e "Команды для управления ботом:"
echo -e "  • Запуск в терминале:       ${YELLOW}./start.sh${NC}"
echo -e "  • Запуск в фоне:            ${YELLOW}./start_background.sh${NC}"
echo -e "  • Остановка фонового бота:  ${YELLOW}./stop.sh${NC}"
echo -e "  • Просмотр логов:           ${YELLOW}tail -f bot.log${NC}"
echo -e "\nОткройте Telegram и отправьте ${CYAN}/start${NC} вашему боту!\n"

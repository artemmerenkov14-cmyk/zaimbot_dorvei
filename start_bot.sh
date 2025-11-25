#!/bin/bash

# Скрипт для запуска Telegram бота займов

echo "=================================="
echo "🤖 Запуск Telegram бота займов"
echo "=================================="
echo ""

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не установлен!"
    echo "Установите Python3: sudo apt install python3"
    exit 1
fi

echo "✅ Python3 найден: $(python3 --version)"

# Проверка наличия pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 не установлен!"
    echo "Установите pip3: sudo apt install python3-pip"
    exit 1
fi

echo "✅ pip3 найден"

# Проверка установки зависимостей
echo ""
echo "🔍 Проверка зависимостей..."

if ! pip3 show aiogram &> /dev/null; then
    echo "⚠️  aiogram не установлен!"
    echo "📦 Устанавливаю зависимости..."
    pip3 install -r requirements.txt

    if [ $? -ne 0 ]; then
        echo "❌ Ошибка установки зависимостей!"
        exit 1
    fi
    echo "✅ Зависимости установлены"
else
    echo "✅ Все зависимости установлены"
fi

# Проверка наличия токена
echo ""
echo "🔑 Проверка токена бота..."

if grep -q "YOUR_BOT_TOKEN_HERE" loan_bot.py; then
    echo "⚠️  ВНИМАНИЕ: Вы не заменили токен бота!"
    echo ""
    echo "📝 Инструкция:"
    echo "1. Получите токен у @BotFather в Telegram"
    echo "2. Откройте файл loan_bot.py"
    echo "3. Замените 'YOUR_BOT_TOKEN_HERE' на ваш токен"
    echo ""
    read -p "❓ Продолжить запуск? (y/n): " answer
    if [ "$answer" != "y" ]; then
        echo "Запуск отменен"
        exit 0
    fi
fi

# Запуск бота
echo ""
echo "=================================="
echo "🚀 Запускаю бота..."
echo "=================================="
echo "Нажмите Ctrl+C для остановки"
echo ""

python3 loan_bot.py

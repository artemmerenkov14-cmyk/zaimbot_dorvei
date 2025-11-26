#!/bin/bash

# Скрипт для запуска всех ботов одновременно

echo "=================================="
echo "🤖 Запуск всех ботов"
echo "=================================="
echo ""

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не установлен!"
    exit 1
fi

echo "✅ Python3 найден: $(python3 --version)"

# Проверка зависимостей
if ! pip3 show aiogram &> /dev/null; then
    echo "⚠️  Установка зависимостей..."
    pip3 install -r requirements.txt
fi

echo ""
echo "=================================="
echo "🚀 Запускаю ботов..."
echo "=================================="
echo ""

# Запуск основного бота в фоне
echo "▶️  Запуск основного бота (loan_bot.py)..."
python3 loan_bot.py &
LOAN_BOT_PID=$!
echo "✅ Основной бот запущен (PID: $LOAN_BOT_PID)"

# Небольшая пауза
sleep 2

# Запуск статистического бота в фоне
echo "▶️  Запуск статистического бота (stats_bot.py)..."
python3 stats_bot.py &
STATS_BOT_PID=$!
echo "✅ Статистический бот запущен (PID: $STATS_BOT_PID)"

echo ""
echo "=================================="
echo "✅ Все боты запущены!"
echo "=================================="
echo "📊 Основной бот: PID $LOAN_BOT_PID"
echo "📈 Статистический бот: PID $STATS_BOT_PID"
echo ""
echo "ℹ️  Для остановки нажмите Ctrl+C"
echo "ℹ️  Или используйте: kill $LOAN_BOT_PID $STATS_BOT_PID"
echo "=================================="
echo ""

# Функция для остановки ботов при Ctrl+C
cleanup() {
    echo ""
    echo "⏹️  Останавливаю ботов..."
    kill $LOAN_BOT_PID 2>/dev/null
    kill $STATS_BOT_PID 2>/dev/null
    echo "✅ Боты остановлены"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Ожидаем завершения процессов
wait

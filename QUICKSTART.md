# 🚀 Быстрый старт бота

## За 5 минут до запуска!

### Шаг 1: Установите зависимости

```bash
pip install -r requirements.txt
```

### Шаг 2: Получите токен бота

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте `/newbot`
3. Введите имя бота (например: "Займы бот")
4. Введите username бота (например: "my_loan_bot")
5. Скопируйте токен (выглядит так: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Шаг 3: Добавьте токен в бота

Откройте `loan_bot.py` и замените:

```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
```

на:

```python
BOT_TOKEN = "ВАШ_ТОКЕН_КОТОРЫЙ_ВЫ_СКОПИРОВАЛИ"
```

### Шаг 4: Запустите бота

```bash
python loan_bot.py
```

### Шаг 5: Проверьте работу

1. Найдите вашего бота в Telegram по username
2. Нажмите "Start" или отправьте `/start`
3. Выберите страну
4. Проверьте, что ссылки работают

## ✅ Готово!

Ваш бот запущен и готов к работе!

---

## 🔧 Дополнительные настройки

### Использование переменных окружения (рекомендуется)

1. Скопируйте `.env.example` в `.env`:
   ```bash
   cp .env.example .env
   ```

2. Отредактируйте `.env` и добавьте свой токен:
   ```
   BOT_TOKEN=ВАШ_ТОКЕН
   ```

3. Установите python-dotenv:
   ```bash
   pip install python-dotenv
   ```

4. В начале `loan_bot.py` добавьте:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

### Включение прокси (если нужно)

В `loan_bot.py` измените:

```python
USE_PROXY = True
```

И укажите данные вашего прокси сервера.

---

## 📝 Troubleshooting

**Бот не запускается?**
- Проверьте токен
- Убедитесь, что установлены зависимости: `pip list | grep aiogram`

**Ошибка "Invalid token"?**
- Токен скопирован неправильно
- Проверьте, что токен в формате `NUMBER:LETTERS`

**Кнопки не работают?**
- Обновите aiogram: `pip install --upgrade aiogram`

---

## 📞 Нужна помощь?

Проверьте полную документацию в `README_BOT.md`

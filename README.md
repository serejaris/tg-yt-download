<!-- hq-readme-ru: 2026-05-09 -->
# tg-yt-download

Коротко: Telegram-проект или бот по теме «tg yt download».

## Что здесь

- Назначение: Telegram-проект или бот по теме «tg yt download».
- Основной стек: Python.
- Видимость: публичный репозиторий.
- Статус: активный репозиторий; актуальность проверять по issues и последним коммитам.

## Где смотреть работу

- Задачи и текущие решения: GitHub Issues этого репозитория.
- Код и материалы: файлы в корне и профильные папки проекта.
- Связь с HQ: если проект влияет на продукт, контент или воронку, сверяйте канон в `0_hq` и репозитории-владельце.

## Для агентов

- Сначала прочитайте этот README и открытые issues.
- Не переносите сюда канон соседних проектов без ссылки на источник.
- Перед правками проверьте существующие scripts, package.json/pyproject и локальные инструкции.

---

## Исходный README

# 🎵 YouTube Audio Downloader Bot

Telegram бот для скачивания аудио с YouTube в форматах MP3 и WAV.

## Возможности

- ✅ Скачивание аудио с YouTube видео
- ✅ Поддержка форматов MP3 (320 kbps) и WAV (lossless)
- ✅ Автоматическая конвертация
- ✅ Информация о видео перед скачиванием
- ✅ Поддержка обычных видео и Shorts

## Требования

- Python 3.10+
- FFmpeg (обязательно!)

## Установка

### 1. Клонирование / Скачивание

```bash
git clone https://github.com/serejaris/tg-yt-download.git
cd tg-yt-download
```

### 2. Установка FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Скачай с https://ffmpeg.org/download.html и добавь в PATH

### 3. Установка Python-зависимостей

**С помощью uv (рекомендуется):**
```bash
# Установка uv (если не установлен)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Установка зависимостей
uv pip install -r requirements.txt
```

**Или с помощью pip:**
```bash
pip install -r requirements.txt
```

### 4. Настройка токена бота

Получи токен у [@BotFather](https://t.me/BotFather) в Telegram.

**Вариант 1 - Переменная окружения:**
```bash
export BOT_TOKEN="your_token_here"
```

**Вариант 2 - В коде:**
Замени `YOUR_BOT_TOKEN_HERE` в файле `bot.py`

### 5. Запуск

**С помощью uv (рекомендуется):**
```bash
uv run --with aiogram --with yt-dlp --with python-dotenv bot.py
```

**Или с помощью python:**
```bash
python bot.py
```

## Использование

1. Открой бота в Telegram
2. Отправь ссылку на YouTube видео
3. Выбери формат (MP3 или WAV)
4. Получи аудио файл!

## Поддерживаемые ссылки

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/shorts/VIDEO_ID`

## Ограничения

- Максимальный размер файла: 50 MB (лимит Telegram)
- Длинные видео в формате WAV могут превысить лимит

## Структура проекта

```
youtube-audio-bot/
├── bot.py              # Основной код бота
├── requirements.txt    # Зависимости
├── README.md          # Документация
└── downloads/         # Временная папка для файлов (создаётся автоматически)
```

## Решение проблем

**"FFmpeg not found"**
- Убедись, что FFmpeg установлен и доступен в PATH

**"File too large"**
- Используй MP3 вместо WAV
- Выбери более короткое видео

**"Could not extract info"**
- Проверь правильность ссылки
- Видео может быть приватным или удалённым

## Лицензия

MIT

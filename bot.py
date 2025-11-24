import os
import re
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router, F

# Загрузка переменных из .env файла
load_dotenv()
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import yt_dlp

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота (замени на свой)
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Папка для временных файлов
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Максимальный размер файла для Telegram (50 MB)
MAX_FILE_SIZE = 50 * 1024 * 1024

# Инициализация
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()


class DownloadState(StatesGroup):
    waiting_for_format = State()


def is_youtube_url(url: str) -> bool:
    """Проверка, является ли ссылка YouTube URL"""
    youtube_patterns = [
        r'(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+',
        r'(https?://)?(www\.)?youtu\.be/[\w-]+',
        r'(https?://)?(www\.)?youtube\.com/shorts/[\w-]+',
    ]
    return any(re.match(pattern, url) for pattern in youtube_patterns)


def extract_video_id(url: str) -> str | None:
    """Извлечение ID видео из URL"""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)([\w-]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


async def get_video_info(url: str) -> dict | None:
    """Получение информации о видео"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=False)
            return info
    except Exception as e:
        logger.error(f"Ошибка получения информации: {e}")
        return None


async def download_audio(url: str, format_type: str, user_id: int) -> tuple[Path | None, str | None]:
    """Скачивание аудио с YouTube"""
    
    output_template = str(DOWNLOAD_DIR / f"{user_id}_%(title)s.%(ext)s")
    
    # Настройки для mp3 и wav
    if format_type == "mp3":
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'quiet': True,
            'no_warnings': True,
        }
    else:  # wav
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
            }],
            'quiet': True,
            'no_warnings': True,
        }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=True)
            
            # Находим скачанный файл
            title = info.get('title', 'audio')
            # Очищаем название от недопустимых символов
            safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)
            
            # Ищем файл
            for file in DOWNLOAD_DIR.iterdir():
                if file.name.startswith(str(user_id)) and file.suffix == f'.{format_type}':
                    return file, title
            
            # Альтернативный поиск
            expected_path = DOWNLOAD_DIR / f"{user_id}_{safe_title}.{format_type}"
            if expected_path.exists():
                return expected_path, title
                
            # Поиск любого подходящего файла
            for file in DOWNLOAD_DIR.iterdir():
                if str(user_id) in file.name:
                    return file, title
                    
            return None, None
            
    except Exception as e:
        logger.error(f"Ошибка скачивания: {e}")
        return None, str(e)


def cleanup_user_files(user_id: int):
    """Удаление временных файлов пользователя"""
    for file in DOWNLOAD_DIR.iterdir():
        if file.name.startswith(str(user_id)):
            try:
                file.unlink()
            except Exception as e:
                logger.error(f"Ошибка удаления файла: {e}")


def format_duration(seconds: int) -> str:
    """Форматирование длительности"""
    if not seconds:
        return "Неизвестно"
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


# Хэндлеры

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработка команды /start"""
    await message.answer(
        "🎵 <b>YouTube Audio Downloader</b>\n\n"
        "Я помогу скачать аудио с YouTube в форматах MP3 или WAV.\n\n"
        "📝 <b>Как использовать:</b>\n"
        "Просто отправь мне ссылку на YouTube видео, и я предложу выбрать формат.\n\n"
        "📎 <b>Поддерживаемые ссылки:</b>\n"
        "• youtube.com/watch?v=...\n"
        "• youtu.be/...\n"
        "• youtube.com/shorts/...\n\n"
        "⚠️ Максимальный размер файла: 50 MB",
        parse_mode=ParseMode.HTML
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработка команды /help"""
    await message.answer(
        "📖 <b>Справка</b>\n\n"
        "<b>Команды:</b>\n"
        "/start - Начать работу\n"
        "/help - Показать справку\n\n"
        "<b>Форматы:</b>\n"
        "🎧 <b>MP3</b> - Сжатый формат, меньший размер файла (320 kbps)\n"
        "🎼 <b>WAV</b> - Несжатый формат, лучшее качество, больший размер\n\n"
        "<b>Ограничения:</b>\n"
        "• Максимальный размер файла: 50 MB\n"
        "• Длинные видео могут превысить лимит в формате WAV",
        parse_mode=ParseMode.HTML
    )


@router.message(F.text)
async def handle_url(message: Message, state: FSMContext):
    """Обработка URL"""
    url = message.text.strip()
    
    if not is_youtube_url(url):
        await message.answer(
            "❌ Это не похоже на ссылку YouTube.\n"
            "Отправь ссылку в формате:\n"
            "• youtube.com/watch?v=...\n"
            "• youtu.be/..."
        )
        return
    
    status_msg = await message.answer("🔍 Получаю информацию о видео...")
    
    # Получаем информацию о видео
    info = await get_video_info(url)
    
    if not info:
        await status_msg.edit_text("❌ Не удалось получить информацию о видео. Проверь ссылку.")
        return
    
    title = info.get('title', 'Без названия')
    duration = info.get('duration', 0)
    channel = info.get('channel', 'Неизвестно')
    thumbnail = info.get('thumbnail', '')
    
    # Сохраняем URL в состоянии
    await state.update_data(url=url, title=title)
    
    # Создаём клавиатуру выбора формата
    builder = InlineKeyboardBuilder()
    builder.button(text="🎧 MP3 (320 kbps)", callback_data="format_mp3")
    builder.button(text="🎼 WAV (lossless)", callback_data="format_wav")
    builder.adjust(1)
    
    await status_msg.edit_text(
        f"🎬 <b>{title}</b>\n\n"
        f"📺 Канал: {channel}\n"
        f"⏱ Длительность: {format_duration(duration)}\n\n"
        f"Выбери формат для скачивания:",
        parse_mode=ParseMode.HTML,
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data.startswith("format_"))
async def handle_format_choice(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора формата"""
    format_type = callback.data.replace("format_", "")
    
    data = await state.get_data()
    url = data.get('url')
    title = data.get('title', 'audio')
    
    if not url:
        await callback.answer("❌ Сессия истекла. Отправь ссылку заново.")
        return
    
    await callback.answer()
    
    format_emoji = "🎧" if format_type == "mp3" else "🎼"
    await callback.message.edit_text(
        f"{format_emoji} Скачиваю <b>{title}</b>\n"
        f"Формат: {format_type.upper()}\n\n"
        f"⏳ Это может занять некоторое время...",
        parse_mode=ParseMode.HTML
    )
    
    # Скачиваем аудио
    user_id = callback.from_user.id
    file_path, result = await download_audio(url, format_type, user_id)
    
    if not file_path or not file_path.exists():
        await callback.message.edit_text(
            f"❌ Ошибка скачивания:\n{result}\n\n"
            "Попробуй другое видео или формат."
        )
        cleanup_user_files(user_id)
        await state.clear()
        return
    
    # Проверяем размер файла
    file_size = file_path.stat().st_size
    
    if file_size > MAX_FILE_SIZE:
        await callback.message.edit_text(
            f"❌ Файл слишком большой ({file_size / 1024 / 1024:.1f} MB).\n"
            f"Лимит Telegram: 50 MB.\n\n"
            f"💡 Попробуй формат MP3 или более короткое видео."
        )
        cleanup_user_files(user_id)
        await state.clear()
        return
    
    # Отправляем файл
    await callback.message.edit_text("📤 Отправляю файл...")
    
    try:
        audio_file = FSInputFile(file_path, filename=f"{title}.{format_type}")
        
        await bot.send_audio(
            chat_id=callback.message.chat.id,
            audio=audio_file,
            title=title,
            caption=f"🎵 {title}\n📁 Формат: {format_type.upper()}\n📊 Размер: {file_size / 1024 / 1024:.1f} MB"
        )
        
        await callback.message.delete()
        
    except Exception as e:
        logger.error(f"Ошибка отправки: {e}")
        await callback.message.edit_text(
            f"❌ Ошибка отправки файла:\n{str(e)}"
        )
    
    finally:
        # Очищаем временные файлы
        cleanup_user_files(user_id)
        await state.clear()


async def main():
    """Запуск бота"""
    dp.include_router(router)
    
    logger.info("Бот запускается...")
    
    # Удаляем webhook если был
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запускаем polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

import os
import logging
import time
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Настройки ---
TOKEN = os.getenv("7622015528:AAEsScVYNYDtPpp7KGfw0qjyfMYH5NEaiBo")  # Берём токен из переменных окружения Render
IMAGE_PATH = "payment_image.jpg"  # Путь к изображению

# --- Логирование ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Обработчики команд ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await update.message.reply_text("Привет! Напиши любое слово, и я дам тебе код для оплаты.")
    except Exception as e:
        logger.error(f"Ошибка в start(): {e}", exc_info=True)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # Проверяем, есть ли текст в сообщении
        if not update.message or not update.message.text:
            logger.warning("Получено пустое сообщение")
            return

        # Отправляем текст с кодом
        await update.message.reply_text(
            "Ты участвуешь! Вот код для оплаты: **1234-5678-9012**",
            parse_mode="Markdown"
        )
        
        # Отправляем изображение с проверкой
        if not os.path.exists(IMAGE_PATH):
            logger.error(f"Файл {IMAGE_PATH} не найден!")
            await update.message.reply_text("⚠️ Изображение временно недоступно")
            return

        with open(IMAGE_PATH, 'rb') as photo:
            await update.message.reply_photo(photo=InputFile(photo))
            
    except Exception as e:
        logger.critical(f"Критическая ошибка в handle_message(): {e}", exc_info=True)
        if update.message:
            await update.message.reply_text("🚫 Произошла ошибка. Попробуйте позже.")

# --- Глобальный обработчик ошибок ---
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Глобальная ошибка: {context.error}", exc_info=True)
    if update and hasattr(update, 'message'):
        await update.message.reply_text("😞 Что-то пошло не так. Мы уже работаем над исправлением!")

# --- Запуск бота ---
def main() -> None:
    # Задержка для инициализации (актуально для Render)
    time.sleep(5)
    
    try:
        # Создаем Application
        application = Application.builder().token(TOKEN).build()
        
        # Регистрируем обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Регистрируем обработчик ошибок
        application.add_error_handler(error_handler)
        
        logger.info("Бот успешно запущен")
        application.run_polling(drop_pending_updates=True)  # Игнорируем старые сообщения
        
    except Exception as e:
        logger.critical(f"ФАТАЛЬНАЯ ОШИБКА ПРИ ЗАПУСКЕ: {e}", exc_info=True)
    finally:
        logger.info("Бот остановлен")

if __name__ == '__main__':
    main()
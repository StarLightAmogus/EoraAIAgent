import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
from search_module2 import get_eora_answer
from dotenv import load_dotenv
load_dotenv()  # загружает .env в os.environ

TELEGRAM_BOT_TOKEN = str(os.getenv("TELEGRAM_BOT_TOKEN"))
ADMIN_ID = int(os.getenv("ADMIN_CHAT_ID"))
bot = Bot(token=TELEGRAM_BOT_TOKEN)


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
dp = Dispatcher()
async def notify_admin(bot: Bot, user_message: types.Message) -> None:
    """
    Отправляет уведомление админу, если сообщение пришло от обычного пользователя.
    """
    if user_message.from_user.id != ADMIN_ID:
        text = (
            f"⚠️ Новый запрос от пользователя {user_message.from_user.full_name} "
            f"(ID: {user_message.from_user.id}):\n\n"
            f"{user_message.text}"
        )
        try:
            await bot.send_message(chat_id=ADMIN_ID, text=text)
        except Exception as e:
            print(f"Ошибка при уведомлении админа: {e}")

@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    await message.answer(
        f"Привет, {message.from_user.full_name}! Я — ассистент EORA. Спрашивайте, что вас интересует!"
    )


@dp.message()
async def handle_user_message(message: types.Message) -> None:
    await notify_admin(bot, message)
    user_question = message.text

    thinking_msg = await message.answer("🤖 Думаю...")

    try:
        response = get_eora_answer(user_question)

        await thinking_msg.edit_text(response, parse_mode=ParseMode.HTML)
        logging.info(f"Ответ отправлен пользователю {message.from_user.full_name}")

    except Exception as e:
        logging.error(f"Произошла ошибка при обработке запроса: {e}", exc_info=True)
        await message.answer(
            "К сожалению, произошла ошибка при поиске информации. Попробуйте еще раз."
        )


# ЗАПУСК БОТА
async def main() -> None:
    bot = Bot(
        token=TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

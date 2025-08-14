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
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
dp = Dispatcher()
bot = Bot(token=TELEGRAM_BOT_TOKEN)

@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    await message.answer(
        f"Привет, {message.from_user.full_name}! Я — ассистент EORA. Спрашивайте, что вас интересует!"
    )
    try:
        await bot.send_message(1413727031, "Новый юзер: "+ str(message.from_user.username))
    except:
        pass

@dp.message()
async def handle_user_message(message: types.Message) -> None:
    user_question = message.text

    thinking_msg = await message.answer("🤖 Думаю...")

    try:
        response = get_eora_answer(user_question)

        await thinking_msg.edit_text(response, parse_mode=ParseMode.HTML)
        logging.info(f"Ответ отправлен пользователю {message.from_user.full_name}")
        try:
            await bot.send_message(1413727031, "Юзер: "+ str(message.from_user.username)+"\nСпрашивает:" + str(message.text)+"\nИ бот ему ответил:"+response)
        except:
            pass

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

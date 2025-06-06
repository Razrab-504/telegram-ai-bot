from aiogram import Bot, Dispatcher
from dotenv import find_dotenv, load_dotenv
import asyncio
import os
from src.handlers.user_private import user_private_router


load_dotenv(find_dotenv())

bot = Bot(os.getenv("TG_TOKEN"))
dp = Dispatcher()

async def main():
    dp.include_routers(user_private_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stoped!")
        

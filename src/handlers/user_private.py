from aiogram import Router, F, Bot, types
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import asyncio
import tempfile
import os

from src.AI.generate import generate, speech_to_text
from src.DB.db_of_users_chat import add_message, get_user_history, trim_user_history

user_private_router = Router()

class Gen(StatesGroup):
    wait = State()

user_histories = {}

async def process_user_input(
    user_id: int,
    text: str,
    message: Message,
    state: FSMContext
):
    await message.answer("Ваш запрос генерируется...")

    history = get_user_history(user_id)

    history.append({"role": "user", "content": text})
    add_message(user_id, "user", text)

    trim_user_history(user_id)

    try:
        response = await generate(history)
        add_message(user_id, "assistant", response)
        await message.answer(response, parse_mode='Markdown')
    except Exception as e:
        await message.answer(f"⚠️ Ошибка: {str(e)}")
    finally:
        await state.clear()


@user_private_router.message(CommandStart())
async def start_cmd(message: Message):
    user_id = message.from_user.id
    
    start_text = (
    "👋 Привет!\n"
    "Я — твой личный AI-ассистент на базе DeepSeek.\n\n"
    "⚡ Что я умею:\n"
    "— Отвечаю на любые вопросы\n"
    "— Объясняю сложные темы простыми словами\n"
    "— Пишу тексты, коды, идеи и сценарии\n"
    "— Помогаю учиться, работать и развиваться\n\n"
    "🧠 Просто напиши свой вопрос — и я сразу отвечу!"
)

    
    await message.answer(start_text)
    

@user_private_router.message(Gen.wait)
async def cmd_stop(message: Message):
    await message.answer("Подождите ваш запрос генерируется!")

    
@user_private_router.message(F.text)
async def cmd_gen(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text
    await state.set_state(Gen.wait)
    await process_user_input(
        user_id=user_id,
        text=text,
        message=message,
        state=state
    )

@user_private_router.message(F.voice)
async def handle_voice_message(message: types.Message, state: FSMContext):
    # Скачиваем голосовое сообщение
    voice = message.voice
    file = await message.bot.get_file(voice.file_id)
    file_path = file.file_path
    await message.bot.download_file(file_path, "audio.ogg")

    user_id = message.from_user.id
    text = speech_to_text()
    await state.set_state(Gen.wait)

    await process_user_input(
        user_id=None,
        text=text,
        message=message,
        state=state
    )

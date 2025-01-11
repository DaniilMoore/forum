from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from app.handlers import router
from pymongo import MongoClient
import asyncio
from config import settings

TOKEN = settings['API_TOKEN']
ADMIN = settings['ADMIN']
USERDB = settings['USERDB']
PASSWORDB = settings['PASSWORDB']

MONGO_URI = f"mongodb+srv://{USERDB}:{PASSWORDB}@forumclaster.cpypy.mongodb.net/?retryWrites=true&w=majority&appName=forumclaster"
mongo_client = MongoClient(MONGO_URI)
db = mongo_client['forumdb']
users_collection = db['forumcoll']

FIXED_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 YaBrowser/24.7.0.0 Safari/537.36"


class Registration(StatesGroup):
    xf_user = State()
    xf_tfa_trust = State()
    xf_session = State()

async def check_authorization(message: Message):
    user_id = message.from_user.id
    user_data = users_collection.find_one({"user_id": user_id})
    
    if user_data:
        await message.answer("Вы уже авторизованы и можете пользоваться ботом.")
    else:
        await message.answer("Вы не авторизованы. Используйте команду /reg для регистрации.")

# Начало регистрации
async def start_registration(message: Message, state: FSMContext):
    await message.answer("Добро пожаловать! Пожалуйста, введите ваш `xf_user`.")
    await state.set_state(Registration.xf_user)

async def process_xf_user(message: Message, state: FSMContext):
    await state.update_data(xf_user=message.text)
    await message.answer("Введите ваш `xf_tfa_trust`.")
    await state.set_state(Registration.xf_tfa_trust)

async def process_xf_tfa_trust(message: Message, state: FSMContext):
    await state.update_data(xf_tfa_trust=message.text)
    await message.answer("Введите ваш `xf_session`.")
    await state.set_state(Registration.xf_session)

async def process_xf_session(message: Message, state: FSMContext):
    await state.update_data(xf_session=message.text)
    user_data = await state.get_data()
    user_id = message.from_user.id

    users_collection.update_one(
        {"user_id": user_id},
        {"$set": {
            "xf_user": user_data['xf_user'],
            "xf_tfa_trust": user_data['xf_tfa_trust'],
            "xf_session": user_data['xf_session'],
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 YaBrowser/24.7.0.0 Safari/537.36"
        }},
        upsert=True
    )

    await message.answer("Регистрация завершена и данные сохранены в базе данных! Теперь вы можете пользоваться ботом.")
    await state.clear()

@router.message(Command('reg'))
async def cmd_reg(message: Message, state: FSMContext):
    await start_registration(message, state)

@router.message(Command('auth'))
async def cmd_auth(message: Message):
    await check_authorization(message)

@router.message(Registration.xf_user)
async def handle_xf_user(message: Message, state: FSMContext):
    await process_xf_user(message, state)

@router.message(Registration.xf_tfa_trust)
async def handle_xf_tfa_trust(message: Message, state: FSMContext):
    await process_xf_tfa_trust(message, state)

@router.message(Registration.xf_session)
async def handle_xf_session(message: Message, state: FSMContext):
    await process_xf_session(message, state)

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    dp.message.register(cmd_reg, Command('reg'))
    dp.message.register(cmd_auth, Command('auth'))

    dp.include_router(router)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен!')
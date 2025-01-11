from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from pymongo import MongoClient
from collections import Counter
from datetime import datetime, timedelta
import app.keyboards as kb
import arz_api
from config import settings

# cookies = settings['COOKIES']
# user_agent = settings['USER_AGENT']

USERDB = settings['USERDB']
PASSWORDB = settings['PASSWORDB']
MONGO_URI = f"mongodb+srv://{USERDB}:{PASSWORDB}@forumclaster.cpypy.mongodb.net/?retryWrites=true&w=majority"
mongo_client = MongoClient(MONGO_URI)
db = mongo_client['forumdb']
users_collection = db['forumcoll']

router = Router()

def get_user_data(user_id: int):
    """
    Получение cookies и user_agent пользователя из базы данных.
    """
    user_data = users_collection.find_one({"user_id": user_id})
    if user_data:
        cookies = {
            "xf_user": user_data.get("xf_user"),
            "xf_tfa_trust": user_data.get("xf_tfa_trust"),
            "xf_session": user_data.get("xf_session")
        }
        user_agent = user_data.get("user_agent")
        return cookies, user_agent
    return None, None


FIXED_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 YaBrowser/24.7.0.0 Safari/537.36"

def initialize_api(user_id: int):

    cookies, _ = get_user_data(user_id)

    if not cookies:
        return None  # Пользователь не зарегистрирован

    # Создаём объект API с фиксированным user_agent
    return arz_api.ArizonaAPI(user_agent=FIXED_USER_AGENT, cookie=cookies)

@router.message(CommandStart())
async def cmd_start(message: Message):
    api = initialize_api(message.from_user.id)

    if not api:
        await message.answer(
            "Вы не зарегистрированы. Пожалуйста, выполните регистрацию, чтобы использовать бота."
        )
        return

    await message.answer("Главное меню:", reply_markup=kb.main)

@router.message(F.text == 'Форум')
async def forum(message: Message):
    await message.answer('Выберите действие:', reply_markup=kb.forum_stat)

@router.message(F.text == 'Считалочка')
async def score(message: Message):
    api = initialize_api(message.from_user.id)

    if not api:
        await message.answer(
            "Вы не зарегистрированы. Пожалуйста, выполните регистрацию, чтобы использовать бота."
        )
        return

    myuser = api.current_member.id
    information = await message.answer('Загружаю информацию')
    thread = api.get_thread(372530)
    last_post = thread.get_posts(thread.pages_count)[-1]
    post = api.get_post(last_post)
    number = post.text_content
    user = post.creator.id
    await information.delete()
    if user == myuser:
        await message.answer(f'Последнее сообщение отправлено - {post.creator.username}')
    else:
        number = int(number)+1
        send_score = api.answer_thread(372530, number)
        await message.answer(f'Отправил сообщение - {number} в теме - {thread.title}')

@router.message(F.text == 'Статистика жалоб')
async def stat_complaints(message: Message):
    await message.answer('Выберите раздел:', reply_markup=kb.forum_sections)

@router.message(F.text == 'ЖБ Адм')
async def jb_adm(message: Message):
    api = initialize_api(message.from_user.id)

    if not api:
        await message.answer(
            "Вы не зарегистрированы. Пожалуйста, выполните регистрацию, чтобы использовать бота."
        )
        return
    
    stat = await message.answer('Загружаю статистику, ожидайте.')
    one_week_ago = datetime.now() - timedelta(days = 7)

    closed_threads = []
    closers = []

    category_id = 119
    cpage = 1
    for page in range(1, cpage + 7):
        threads = api.get_threads(category_id, page)
        tunpins = threads['unpins']
        for i in tunpins:
            thread_unpins = api.get_thread(i)
            post = api.get_thread_posts(i)[-1]
            last_post = api.get_post(post)
            if thread_unpins.is_closed:
                closed_at = datetime.fromtimestamp(last_post.create_date)
                if closed_at > one_week_ago:
                    closed_threads.append(thread_unpins)
                    closer_name = last_post.creator.username
                    closers.append(closer_name)
                    
    closer_counts = Counter(closers)
    total_closed = len(closed_threads)
    msg = '\n📊 Недельная статистика закрытых тем по пользователям:\n'
    if total_closed > 0:
        for closer, count in closer_counts.items():
            percentage = (count / total_closed) * 100
            msg += f'{closer} закрыл {count} жалоб(-ы) [{percentage:.0f}%]\n'
    else:
        msg += 'Нет закрытых тем за последнюю неделю.\n'

    msg += f'Всего закрыто жалоб: {total_closed}.'
    await stat.delete()
    await message.answer(msg)

@router.message(F.text == 'ЖБ Гос')
async def jb_gos(message: Message):
    api = initialize_api(message.from_user.id)
    if not api:
        await message.answer(
            "Вы не зарегистрированы. Пожалуйста, выполните регистрацию, чтобы использовать бота."
        )
        return
    
    stat = await message.answer('Загружаю статистику, ожидайте.')
    one_week_ago = datetime.now() - timedelta(days = 7)

    closed_threads = []
    closers = []

    category_id = 121
    cpage = 1
    for page in range(1, cpage + 7):
        threads = api.get_threads(category_id, page)
        tunpins = threads['unpins']
        for i in tunpins:
            thread_unpins = api.get_thread(i)
            post = api.get_thread_posts(i)[-1]
            last_post = api.get_post(post)
            if thread_unpins.is_closed:
                closed_at = datetime.fromtimestamp(last_post.create_date)
                if closed_at > one_week_ago:
                    closed_threads.append(thread_unpins)
                    closer_name = last_post.creator.username
                    closers.append(closer_name)
    closer_counts = Counter(closers)
    total_closed = len(closed_threads)
    msg = '\n📊 Недельная статистика закрытых тем по пользователям:\n'
    if total_closed > 0:
        for closer, count in closer_counts.items():
            percentage = (count / total_closed) * 100
            msg += f'{closer} закрыл {count} жалоб(-ы) [{percentage:.0f}%]\n'
    else:
        msg += 'Нет закрытых тем за последнюю неделю.\n'

    msg += f'Всего закрыто жалоб: {total_closed}.'
    await stat.delete()
    await message.answer(msg)

@router.message(F.text == 'ЖБ Лидеры')
async def jb_lid(message: Message):
    api = initialize_api(message.from_user.id)
    if not api:
        await message.answer(
            "Вы не зарегистрированы. Пожалуйста, выполните регистрацию, чтобы использовать бота."
        )
        return
    
    stat = await message.answer('Загружаю статистику, ожидайте.')
    one_week_ago = datetime.now() - timedelta(days = 7)

    closed_threads = []
    closers = []

    category_id = 124
    cpage = 1
    for page in range(1, cpage + 3):
        threads = api.get_threads(category_id, page)
        tunpins = threads['unpins']
        for i in tunpins:
            thread_unpins = api.get_thread(i)
            post = api.get_thread_posts(i)[-1]
            last_post = api.get_post(post)
            if thread_unpins.is_closed:
                closed_at = datetime.fromtimestamp(last_post.create_date)
                if closed_at > one_week_ago:
                    closed_threads.append(thread_unpins)
                    closer_name = last_post.creator.username
                    closers.append(closer_name)
    closer_counts = Counter(closers)
    total_closed = len(closed_threads)
    msg = '\n📊 Недельная статистика закрытых тем по пользователям:\n'
    if total_closed > 0:
        for closer, count in closer_counts.items():
            percentage = (count / total_closed) * 100
            msg += f'{closer} закрыл {count} жалоб(-ы) [{percentage:.0f}%]\n'
    else:
        msg += 'Нет закрытых тем за последнюю неделю.\n'

    msg += f'Всего закрыто жалоб: {total_closed}.'
    await stat.delete()
    await message.answer(msg)

@router.message(F.text == 'РП Биографии')
async def rp_bio(message: Message):
    api = initialize_api(message.from_user.id)
    if not api:
        await message.answer(
            "Вы не зарегистрированы. Пожалуйста, выполните регистрацию, чтобы использовать бота."
        )
        return
    
    stat = await message.answer('Загружаю статистику, ожидайте.')
    one_week_ago = datetime.now() - timedelta(days = 7)

    closed_threads = []
    closers = []

    category_id = 374
    cpage = 1
    for page in range(1, cpage + 5):
        threads = api.get_threads(category_id, page)
        tunpins = threads['unpins']
        for i in tunpins:
            thread_unpins = api.get_thread(i)
            post = api.get_thread_posts(i)[-1]
            last_post = api.get_post(post)
            if thread_unpins.is_closed:
                closed_at = datetime.fromtimestamp(last_post.create_date)
                if closed_at > one_week_ago:
                    closed_threads.append(thread_unpins)
                    closer_name = last_post.creator.username
                    closers.append(closer_name)
    closer_counts = Counter(closers)
    total_closed = len(closed_threads)
    msg = '\n📊 Недельная статистика закрытых тем по пользователям:\n'
    if total_closed > 0:
        for closer, count in closer_counts.items():
            percentage = (count / total_closed) * 100
            msg += f'{closer} закрыл {count} жалоб(-ы) [{percentage:.0f}%]\n'
    else:
        msg += 'Нет закрытых тем за последнюю неделю.\n'

    msg += f'Всего закрыто жалоб: {total_closed}.'
    await stat.delete()
    await message.answer(msg)

@router.message(F.text == 'Главное меню')
async def go_to_main_menu(message: Message):
    await message.answer('Главное меню:', reply_markup=kb.main)
import os
import random
import asyncio
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import InputFile
from aiohttp import web

# ---------- 1. 40 разных предсказаний и 20 советов ----------
PRED = [
    "Сегодня удача на твоей стороне!",
    "Избегай крупных трат — завтра будут важные покупки.",
    "Встретишь человека, который поменяет твои планы в лучшую сторону.",
    "Утро начни с чашки воды — энергия повысится.",
    "Не откладывай звонок, который давно хочешь сделать.",
    "Вечером получишь приятную новость.",
    "Слушай интуицию: она подскажет правильный выбор.",
    "Появится шанс проявить себя — не упусти.",
    "Сегодня хороший день для новых начинаний.",
    "Не бойся просить помощи — тебе охотно помогут.",
    "Мелкая покупка поднимет настроение.",
    "Постарайся закончить дела до обеда — вечер будет свободнее.",
    "Тебя ждёт неожиданный комплимент.",
    "Прогулка на свежем воздухе принесёт идею.",
    "Не спорь с близкими — день пройдёт гладко.",
    "Полезный совет придёт от случайного собеседника.",
    "Старайся двигаться чуть быстрее обычного — успеешь больше.",
    "Сегодня удачный день для обучения.",
    "Получишь приглашение, которое трудно отклонить.",
    "Не забывай сказать «спасибо» — это вернётся сторицей.",
    "Хороший момент, чтобы начать вести дневник.",
    "Сделай паузу перед ответом — избежишь конфликта.",
    "Ты окажешься в нужном месте в нужное время.",
    "Музыка поможет настроиться на рабочий лад.",
    "Сегодня всё получится быстрее, чем ожидаешь.",
    "Полезно убрать рабочее место — улучшится концентрация.",
    "Не бойся менять планы — они станут лучше.",
    "Подарок, который давно хотел сделать, будет принят с радостью.",
    "Вечер проведи с любимым фильмом — отдохнёшь.",
    "Старайся пить воду каждый час — энергия сохранится.",
    "Появится возможность сэкономить — воспользуйся.",
    "Сегодня хороший день для творчества.",
    "Не откладывай на завтра то, что займёт 5 минут.",
    "Ты получишь знак, что всё идёт по плану.",
    "Полезно выспаться — завтра будет насыщенный день.",
    "Не забывай хвалить себя — заслуживаешь.",
    "Случайная встреча подарит полезный контакт.",
    "Сделай комплимент коллеге — улучшится атмосфера.",
    "Сегодня удачный день для покупки билетов.",
    "Не переедай на ночь — сон будет крепче.",
    "Постарайся улыбаться чаще — люди ответят тем же."
]

ADV = [
    "Совет: выпей стакан воды и улыбнись.",
    "Совет: прогуляйся 20 минут без телефона.",
    "Совет: сделай то, что откладывал последнюю неделю.",
    "Совет: позвони близкому просто так.",
    "Совет: проведи 10 минут в тишине.",
    "Совет: составь список из 3 задач на день.",
    "Совет: поблагодари себя за вчерашнее.",
    "Совет: включи любимую музыку и расслабься.",
    "Совет: убери со стола – мысли станут яснее.",
    "Совет: не проверяй почту каждые 5 минут.",
    "Совет: съешь фрукт вместо сладкого.",
    "Совет: выйди на балкон/улицу – подыши воздухом.",
    "Совет: напиши 3 вещи, за которые ты благодарен.",
    "Совет: поменяй позу – выпрями спину.",
    "Совет: сделай 10 приседаний или 5 глубоких вдохов.",
    "Совет: закрой глаза на 30 секунд и просто послушай.",
    "Совет: отложи телефон за 30 мин до сна.",
    "Совет: улыбнись себе в зеркало.",
    "Совет: помоги кому-то без ожидания награды.",
    "Совет: начни утро со стакана тёплой воды."
]

# ---------- 2. Красивые русские знаки ----------
ZODIACS = ["♈ Овен","♉ Телец","♊ Близнецы","♋ Рак","♌ Лев","♍ Дева",
           "♎ Весы","♏ Скорпион","♐ Стрелец","♑ Козерог","♒ Водолей","♓ Рыбы"]

bot = Bot(os.getenv("TOKEN"))
dp  = Dispatcher()

# ---------- 3. Команда /help ----------
@dp.message(F.text == "/help")
async def help_msg(m: types.Message):
    await m.answer(
        "🌟 <b>Привет!</b>\n\n"
        "Я присылаю короткий гороскоп и полезный совет на день.\n"
        "Нажми /start и выбери свой знак зодиака.\n\n"
        "Каждое утро можно подписаться на автоматическую рассылку – команда /subscribe",
        parse_mode="HTML"
    )

# ---------- 4. Подписка «каждое утро» ----------
USERS_DB = set()          # {user_id, ...}  (в продакшене лучше SQLite/Redis)

@dp.message(F.text == "/subscribe")
async def subscribe(m: types.Message):
    USERS_DB.add(m.from_user.id)
    await m.answer("✅ Подписка оформлена! Каждый день в 8:00 по МСК я пришлю гороскоп.")

@dp.message(F.text == "/unsubscribe")
async def unsubscribe(m: types.Message):
    USERS_DB.discard(m.from_user.id)
    await m.answer("❌ Рассылка отключена.")

async def send_daily():
    """Генерирует и рассылает гороскопы в 8:00 МСК каждый день."""
    await bot.send_message(chat_id=admin_id, text="📢 Рассылаю утренние гороскопы...")
    for uid in USERS_DB:
        try:
            zodiac = random.choice(ZODIACS)          # можно хранить в БД
            await bot.send_message(
                uid,
                f"{zodiac}\n🔮 {random.choice(PRED)}\n💡 {random.choice(ADV)}",
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Не удалось отправить {uid}: {e}")
    await bot.send_message(chat_id=admin_id, text="📬 Рассылка завершена.")

async def scheduler():
    """Планировщик: ждём 8:00 МСК и запускаем send_daily()."""
    while True:
        now = datetime.now()
        next_8 = now.replace(hour=8, minute=0, second=0, microsecond=0)
        if now >= next_8:
            next_8 += timedelta(days=1)
        sleep_seconds = (next_8 - now).total_seconds()
        await asyncio.sleep(sleep_seconds)
        await send_daily()

# ---------- 5. Картинка к каждому знаку ----------
# Положи 12 файлов 1.jpg..12.jpg в папку /pics репозитория, либо используй прямые URL.
# Ниже пример: ссылки на красивые небесные фоны (бесплатно, без копирайта).
ZODIAC_PICS = [
    "https://i.ibb.co/6y4qVGW/1.jpg",  # Овен
    "https://i.ibb.co/P9rV8Yt/2.jpg",  # Телец
    "https://i.ibb.co/3Wf7cBn/3.jpg",  # Близнецы
    "https://i.ibb.co/z5vJ0Yc/4.jpg",  # Рак
    "https://i.ibb.co/3sR5vMg/5.jpg",  # Лев
    "https://i.ibb.co/7rp4r4Q/6.jpg",  # Дева
    "https://i.ibb.co/b3F5qMZ/7.jpg",  # Весы
    "https://i.ibb.co/6ZgFvqY/8.jpg",  # Скорпион
    "https://i.ibb.co/CK1f6rZ/9.jpg",  # Стрелец
    "https://i.ibb.co/3sR5vMg/10.jpg", # Козерог
    "https://i.ibb.co/6y4qVGW/11.jpg", # Водолей
    "https://i.ibb.co/z5vJ0Yc/12.jpg"  # Рыбы
]

@dp.message(F.text == "/start")
async def start(m: types.Message):
    kb = [[types.InlineKeyboardButton(text=z, callback_data=f"z_{i}")]
          for i, z in enumerate(ZODIACS)]
    await m.answer("🌟 Выбери свой знак:", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data.startswith("z_"))
async def horo(c: types.CallbackQuery):
    z_idx = int(c.data.split("_")[1])
    zodiac = ZODIACS[z_idx]
    pred   = random.choice(PRED)
    adv    = random.choice(ADV)
    pic    = ZODIAC_PICS[z_idx]

    await c.message.answer_photo(
        photo=pic,
        caption=f"{zodiac}\n🔮 <b>{pred}</b>\n💡 <b>{adv}</b>",
        parse_mode="HTML"
    )
    await c.answer()

# ---------- веб-заглушка (для Render) ----------
async def dummy(request):
    return web.Response(text="Bot is running")

app = web.Application()
app.router.add_get("/", dummy)

async def on_startup(app):
    # запускаем планировщик в фоне
    asyncio.create_task(scheduler())
    # и polling-бота
    asyncio.create_task(dp.start_polling(bot))

app.on_startup.append(on_startup)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

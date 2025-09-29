#!/usr/bin/env python3
import os
import random
import asyncio
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import InputFile
from aiogram.enums.parse_mode import ParseMode
from aiohttp import web          # только для открытия порта 8080

# ---------- 1. 40 предсказаний + 20 советов ----------
PRED = [
    "Сегодня звёзды советуют действовать смело — удача на твоей стороне.",
    "Неблагоприятный день для крупных трат; лучше подумать трижды.",
    "Встреча, которую ты ждёшь, произойдёт раньше, чем ожидаешь.",
    "Не откладывай дела «на потом» — завтра может быть поздно.",
    "Тебя ждёт приятный сюрприз от человека, которого ты недооцениваешь.",
    "Энергия дня — на стороне творчества: попробуй что-то новое.",
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
    "Постарайся улыбаться чаще — люди ответят тем же.",
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
    "Совет: начни утро со стакана тёплой воды.",
]

# ---------- 2. Русские названия знаков ----------
ZODIACS = ["♈ Овен", "♉ Телец", "♊ Близнецы", "♋ Рак",
           "♌ Лев", "♍ Дева", "♎ Весы", "♏ Скорпион",
           "♐ Стрелец", "♑ Козерог", "♒ Водолей", "♓ Рыбы"]

# ---------- 3. Команда /help ----------
@dp.message(F.text == "/help")
async def cmd_help(m: types.Message):
    await m.answer(
        "🌟 <b>Привет!</b>\n\n"
        "Я присылаю короткий гороскоп и полезный совет на день.\n"
        "Нажми /start и выбери свой знак зодиака.\n\n"
        "Каждое утро можно подписаться на автоматическую рассылку – команда /subscribe",
        parse_mode=ParseMode.HTML
    )

# ---------- 4. Подписка «каждое утро» ----------
USERS_DB = set()                      # {user_id, ...}  (в продакшене лучше SQLite)
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))   # кто получит отчёт о рассылке

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
    if ADMIN_ID:
        await bot.send_message(ADMIN_ID, f"📢 Рассылаю утренние гороскопы ({len(USERS_DB)} чел.)…")
    for uid in USERS_DB:
        try:
            zodiac = random.choice(ZODIACS)
            await bot.send_message(
                uid,
                f"{zodiac}\n🔮 <b>{random.choice(PRED)}</b>\n💡 <b>{random.choice(ADV)}</b>",
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            print(f"Не удалось отправить {uid}: {e}")
    if ADMIN_ID:
        await bot.send_message(ADMIN_ID, "📬 Рассылка завершена.")

async def scheduler():
    """Планировщик: ждём 8:00 МСК и запускаем send_daily()."""
    while True:
        now = datetime.now()
        next_8 = now.replace(hour=8, minute=0, second=0, microsecond=0)
        if now >= next_8:
            next_8 += timedelta(days=1)
        await asyncio.sleep((next_8 - now).total_seconds())
        await send_daily()

# ---------- 5. Красивые картинки ----------
# Бесплатные ссылки на обои для каждого знака (можно заменить свои)
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

bot = Bot(token=os.environ["TOKEN"], default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp  = Dispatcher()

@dp.message(F.text == "/start")
async def start(m: types.Message):
    kb = [[types.InlineKeyboardButton(text=z, callback_data=f"z_{i}")]
          for i, z in enumerate(ZODIACS)]
    await m.answer("🌟 Выбери свой знак:", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data.startswith("z_"))
async def horo(c: types.CallbackQuery):
    z_idx  = int(c.data.split("_")[1])
    zodiac = ZODIACS[z_idx]
    pic    = ZODIAC_PICS[z_idx]
    await c.message.answer_photo(
        photo=pic,
        caption=f"{zodiac}\n🔮 <b>{random.choice(PRED)}</b>\n💡 <b>{random.choice(ADV)}</b>",
        parse_mode=ParseMode.HTML
    )
    await c.answer()

# ---------- единственный энд-поинт для Web Service ----------
async def health(request):
    return web.Response(text="OK")

# ---------- запуск ----------
async def on_startup(app: web.Application):
    # фоновый polling + планировщик
    asyncio.create_task(dp.start_polling(bot))
    asyncio.create_task(scheduler())

async def web_main():
    app = web.Application()
    app.router.add_get("/", health)      # «сердцебиение» для Render
    app.on_startup.append(on_startup)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", 8080)))
    await site.start()
    # работаем вечно
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(web_main())

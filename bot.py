#!/usr/bin/env python3
import os
import random
import asyncio
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, F, types
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiohttp import web

# ---------------- 40 предсказаний + 20 советов ----------------
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

# ---------- 2. Русские знаки ----------
ZODIACS = ["♈ Овен", "♉ Телец", "♊ Близнецы", "♋ Рак",
           "♌ Лев", "♍ Дева", "♎ Весы", "♏ Скорпион",
           "♐ Стрелец", "♑ Козерог", "♒ Водолей", "♓ Рыбы"]

# ---------- 3. /help ----------
async def cmd_help(m: types.Message):
    await m.answer(
        "🌟 <b>Привет!</b>\n\n"
        "Я присылаю короткий гороскоп и полезный совет на день.\n"
        "Нажми /start и выбери свой знак зодиака.\n\n"
        "Каждое утро можно подписаться на автоматическую рассылку – команда /subscribe",
        parse_mode=ParseMode.HTML
    )

# ---------- 4. Подписка «каждое утро» ----------
USERS_DB = set()                      # {user_id, ...}
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))   # кто получит отчёт о рассылке

async def subscribe(m: types.Message):
    USERS_DB.add(m.from_user.id)
    await m.answer("✅ Подписка оформлена! Каждый день в 8:00 по МСК я пришлю гороскоп.")

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

# ---------- единственный энд-поинт для Web Service ----------
async def health(request):
    return web.Response(text="OK")

# ---------- регистрация хэндлеров ----------
def register_handlers(dp: Dispatcher):
    dp.message.register(cmd_help, F.text == "/help")
    dp.message.register(start, F.text == "/start")
    dp.message.register(subscribe, F.text == "/subscribe")
    dp.message.register(unsubscribe, F.text == "/unsubscribe")
    dp.callback_query.register(horo, F.data.startswith("z_"))

async def start(m: types.Message):
    kb = [[types.InlineKeyboardButton(text=z, callback_data=f"z_{i}")]
          for i, z in enumerate(ZODIACS)]
    await m.answer("🌟 Выбери свой знак:", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb))

async def horo(c: types.CallbackQuery):
    z_idx = int(c.data.split("_")[1])
    zodiac = ZODIACS[z_idx]
    text = f"{zodiac}\n🔮 <b>{random.choice(PRED)}</b>\n💡 <b>{random.choice(ADV)}</b>"
    await c.message.answer(text, parse_mode=ParseMode.HTML)
    await c.answer()

# ---------- запуск ----------
bot: Bot

async def on_startup(app: web.Application):
    global bot
    bot = Bot(token=os.environ["TOKEN"], default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    register_handlers(dp)
    # фоновые задачи
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
    await asyncio.Event().wait()         # работаем вечно

if __name__ == "__main__":
    asyncio.run(web_main())

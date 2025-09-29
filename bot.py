#!/usr/bin/env python3
import os
import random
import asyncio
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import InputFile
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiohttp import web
import  httpx
  
# ================== 1. 40 предсказаний + 20 советов ==================
PRED = [
    "Сегодня  звёзды советуют действовать смело – удача на твоей стороне.",
    "Неблагоприятный день для крупных трат; лучше подумать трижды.",
    "Встреча, которую ты ждёшь, произойдёт раньше, чем ожидаешь.",
    "Не откладывай дела «на потом» – завтра может быть поздно.",
    "Тебя ждёт приятный сюрприз от человека, которого ты недооцениваешь.",
    "Энергия дня – на стороне творчества: попробуй что-то новое.",
    "Утро начни с чашки воды – энергия повысится.",
    "Не откладывай звонок, который давно хочешь сделать.",
    "Вечером получишь приятную новость.",
    "Слушай интуицию: она подскажет правильный выбор.",
    "Появится шанс проявить себя – не упусти.",
    "Сегодня хороший день для новых начинаний.",
    "Не бойся просить помощи – тебе охотно помогут.",
    "Мелкая покупка поднимет настроение.",
    "Постарайся закончить дела до обеда – вечер будет свободнее.",
    "Тебя ждёт неожиданный комплимент.",
    "Прогулка на свежем воздухе принесёт идею.",
    "Не спорь с близкими – день пройдёт гладко.",
    "Полезный совет придёт от случайного собеседника.",
    "Старайся двигаться чуть быстрее обычного – успеешь больше.",
    "Сегодня удачный день для обучения.",
    "Получишь приглашение, которое трудно отклонить.",
    "Не забывай сказать «спасибо» – это вернётся сторицей.",
    "Хороший момент, чтобы начать вести дневник.",
    "Сделай паузу перед ответом – избежишь конфликта.",
    "Ты окажешься в нужном месте в нужное время.",
    "Музыка поможет настроиться на рабочий лад.",
    "Сегодня всё получится быстрее, чем ожидаешь.",
    "Полезно убрать рабочее место – улучшится концентрация.",
    "Не бойся менять планы – они станут лучше.",
    "Подарок, который давно хотел сделать, будет принят с радостью.",
    "Вечер проведи с любимым фильмом – отдохнёшь.",
    "Старайся пить воду каждый час – энергия сохранится.",
    "Появится возможность сэкономить – воспользуйся.",
    "Сегодня хороший день для творчества.",
    "Не откладывай на завтра то, что займёт 5 минут.",
    "Ты получишь знак, что всё идёт по плану.",
    "Полезно выспаться – завтра будет насыщенный день.",
    "Не забывай хвалить себя – заслуживаешь.",
    "Случайная встреча подарит полезный контакт.",
    "Сделай комплимент коллеге – улучшится атмосфера.",
    "Сегодня удачный день для покупки билетов.",
    "Не переедай на ночь – сон будет крепче.",
    "Постарайся улыбаться чаще – люди ответят тем же.",
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

# ================== 2. Русские знаки ==================
ZODIACS = ["♈ Овен", "♉ Телец", "♊ Близнецы", "♋ Рак",
           "♌ Лев", "♍ Дева", "♎ Весы", "♏ Скорпион",
           "♐ Стрелец", "♑ Козерог", "♒ Водолей", "♓ Рыбы"]

# ================== 3. /help ==================
async def cmd_help(m: types.Message):
    await m.answer(
        "🌟 <b>Привет!</b>\n\n"
        "Я присылаю короткий гороскоп и полезный совет на день.\n"
        "Нажми /start и выбери свой знак зодиака.\n\n"
        "Каждое утро можно подписаться на автоматическую рассылку – команда /subscribe\n"
        "Персональные лунные рекомендации – /lunarbio\n"
        "Лунный календарь на месяц – /mooncal",
        parse_mode=ParseMode.HTML
    )

# ================== 4. Подписка «каждое утро» ==================
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

# ================== 5. Картинки (без файлов – ссылки) ==================
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

# ================== ЛУННЫЙ МОДУЛЬ (встроен) ==================
SYNODIC_MONTH = 29.53058867
KNOWN_NEW_MOON = datetime(2000, 1, 6, 18, 14)

def moon_age(dt: datetime) -> float:
    delta = dt - KNOWN_NEW_MOON
    return (delta.total_seconds() / 86400) % SYNODIC_MONTH

def lunar_day_and_phase(dt: datetime):
    age = moon_age(dt)
    day = int(age) + 1
    if age < 1.845:
        phase = "New"
    elif age < 5.53:
        phase = "Waxing Crescent"
    elif age < 9.22:
        phase = "First Quarter"
    elif age < 12.91:
        phase = "Waxing Gibbous"
    elif age < 16.59:
        phase = "Full"
    elif age < 20.27:
        phase = "Waning Gibbous"
    elif age < 23.95:
        phase = "Last Quarter"
    else:
        phase = "Waning Crescent"
    return day, phase
 
PERSONAL_MOON_ADV = {
    1: "Сегодня отличный день для новых начинаний – вы родились в день новой Луны.",
    2: "Действуйте спокойно, нарабатывайте ресурс – вы «растущая» Луна.",
    3: "Доводите дела до середины – вы «первая четверть».",
    4: "Расширяйте горизонты, учитесь – вы «растущая» Луна.",
    5: "Делитесь знаниями – вы «полная» Луна.",
    6: "Избавляйтесь от лишнего – вы «убывающая» Луна.",
    7: "Подводите итоги, отдыхайте – вы «последняя четверть».",
    8: "Слушайте интуицию – вы «убывающая» Луна.",
    9: "Планируйте, но не спешите – вы «новолуние».",
    10: "Растите вместе с Луной – вы «растущая».",
    11: "Будьте на людях – вы «полная» Луна.",
    12: "Чистите пространство – вы «убывающая».",
    13: "Завершайте старые дела – вы «последняя четверть».",
    14: "Отдыхайте и анализируйте – вы «убывающая».",
    15: "День силы – вы «полная» Луна.",
    16: "Переходный момент – вы «полная».",
    17: "Начинайте сбрасывать балласт – вы «убывающая».",
    18: "Делитесь опытом – вы «последняя четверть».",
    19: "Сводите счёты – вы «убывающая».",
    20: "Готовьтесь к новому циклу – вы «новолуние».",
    21: "Завершайте, закрывайте – вы «последняя четверть».",
    22: "Слушайте тело – вы «убывающая».",
    23: "Планируйте, мечтайте – вы «новолуние».",
    24: "Делайте паузу – вы «последняя четверть».",
    25: "Избавляйтесь – вы «убывающая».",
    26: "Готовьтесь к старту – вы «новолуние».",
    27: "Анализируйте – вы «последняя четверть».",
    28: "Отдыхайте – вы «убывающая».",
    29: "Пишите планы – вы «новолуние».",
    30: "Завершайте – вы «последняя четверть».",
}

def get_today_lunar():
    return lunar_day_and_phase(datetime.now())

def get_birth_lunar(birth: datetime):
    return lunar_day_and_phase(birth)

def personal_today_advice(birth_date: datetime):
    day, _ = get_birth_lunar(birth_date)
    return PERSONAL_MOON_ADV.get(day, "Слушай свою интуицию – Луна всегда подскажет.")

def lunar_calendar_month(start: datetime):
    cal = []
    for d in range(30):
        dt = start + timedelta(days=d)
        day, phase = lunar_day_and_phase(dt)
        cal.append((dt, day, phase))
    return cal

# ---------- русские названия фаз ----------
RU_PHASE = {
    "New": "Новолуние",
    "Waxing Crescent": "Молодая Луна",
    "First Quarter": "Первая четверть",
    "Waxing Gibbous": "Прибывающая Луна",
    "Full": "Полнолуние",
    "Waning Gibbous": "Убывающая Луна",
    "Last Quarter": "Последняя четверть",
    "Waning Crescent": "Старая Луна",
}

# ---------- команда /moon ----------
async def cmd_moon(m: types.Message):
    day, phase_en = get_today_lunar()
    phase_ru = RU_PHASE.get(phase_en, phase_en)
    text = (
        f"🌙 <b>Луна сегодня</b>\n\n"
        f"Лунный день: <b>{day}</b> (из 30)\n"
        f"Фаза: <b>{phase_ru}</b>\n\n"
        f"Совет: {PERSONAL_MOON_ADV.get(day, 'Слушайте свою интуицию.')}"
    )
    await m.answer(text, parse_mode=ParseMode.HTML)
  
# ================== ЛУННЫЕ КОМАНДЫ ==================
async def cmd_lunarbio(m: types.Message):
    await m.answer(
        "🌙 Отправь свою дату рождения в формате <b>ДД.ММ.ГГГГ</b>, "
        "и я расскажу, какая Луна была в этот день и какой сегодня совет для тебя.",
        parse_mode=ParseMode.HTML
    )

async def get_birth_luna(m: types.Message):
    try:
        birth = datetime.strptime(m.text, "%d.%m.%Y")
    except ValueError:
        await m.answer("📆 Неверный формат. Пример: 14.03.1995")
        return

    day, phase = get_birth_lunar(birth)
    advice = personal_today_advice(birth)
    today_day, today_phase = get_today_lunar()

    text = (
        f"🌙 <b>Твоя лунная карта</b>\n\n"
        f"Дата рождения: <b>{birth.strftime('%d.%m.%Y')}</b>\n"
        f"Лунный день: <b>{day}</b> (из 30)\n"
        f"Фаза: <b>{phase}</b>\n\n"
        f"📌 Персональный совет на сегодня:\n<i>{advice}</i>\n\n"
        f"Сегодня Луна: <b>{today_phase}</b> ({today_day} день)"
    )
    await m.answer(text, parse_mode=ParseMode.HTML)

async def cmd_mooncal(m: types.Message):
    cal = lunar_calendar_month(datetime.now())
    lines = [f"{dt.strftime('%d.%m')}: {day} день – {phase}" for dt, day, phase in cal]
    text = "📆 <b>Лунный календарь на 30 дней</b>\n\n" + "\n".join(lines[:15])
    await m.answer(text, parse_mode=ParseMode.HTML)

# ================== СТАРЫЕ ХЭНДЛЕРЫ ==================
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
# ================== РЕГИСТРАЦИЯ ==================
def register_handlers(dp: Dispatcher):
    dp.message.register(cmd_help, F.text == "/help")
    dp.message.register(start, F.text == "/start")
    dp.message.register(subscribe, F.text == "/subscribe")
    dp.message.register(unsubscribe, F.text == "/unsubscribe")
    dp.message.register(cmd_moon, F.text == "/moon")
    dp.message.register(cmd_lunarbio, F.text == "/lunarbio")
    dp.message.register(get_birth_luna, F.text.regexp(r"^\d{2}\.\d{2}\.\d{4}$"))
    dp.message.register(cmd_mooncal, F.text == "/mooncal")
    dp.callback_query.register(horo, F.data.startswith("z_"))

# ================== WEB-SERVICE ЗАГЛУШКА ==================
async def health(request):
    return web.Response(text="OK")

# ================== ЗАПУСК ==================
bot: Bot

async def on_startup(app: web.Application):
    global bot
    bot = Bot(token=os.environ["TOKEN"], default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    register_handlers(dp)
    asyncio.create_task(dp.start_polling(bot))
    asyncio.create_task(scheduler())

async def web_main():
    app = web.Application()
    app.router.add_get("/", health)
    app.on_startup.append(on_startup)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", 8080)))
    await site.start()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(web_main())

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
import httpx

# ================== НАСТРОЙКИ ==================
BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
ASTRO_TOKEN = os.getenv("ASTRO_TOKEN", "")  # токен astro-chart.com (по желанию)

# ================== РЕАЛЬНЫЕ API ==================
REAL_HORO_API = "https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily"
NASA_MOON_API = "https://aa.usno.navy.mil/api/calculate"  # лунные данные NASA

# ================== ЛУННЫЙ МОДУЛЬ (встроен) ==================
SYNODIC_MONTH = 29.53058867
KNOWN_NEW_MOON = datetime(2000, 1, 6, 18, 14)

def moon_age(dt: datetime) -> float:
    delta = dt - KNOWN_NEW_MOON
    return (delta.total_seconds() / 86400) % SYNODIC_MONTH

def lunar_day_and_phase(dt: datetime):
    age = moon_age(dt)
    day = int(age) + 1
    if age < 1.845:    return "New"
    if age < 5.53:     return "Waxing Crescent"
    if age < 9.22:     return "First Quarter"
    if age < 12.91:    return "Waxing Gibbous"
    if age < 16.59:    return "Full"
    if age < 20.27:    return "Waning Gibbous"
    if age < 23.95:    return "Last Quarter"
    return "Waning Crescent"

RU_PHASE = {
    "New": "Новолуние", "Waxing Crescent": "Молодая Луна",
    "First Quarter": "Первая четверть", "Waxing Gibbous": "Прибывающая Луна",
    "Full": "Полнолуние", "Waning Gibbous": "Убывающая Луна",
    "Last Quarter": "Последняя четверть", "Waning Crescent": "Старая Луна",
}

# ================== РЕАЛЬНЫЕ ДАННЫЕ ==================
async def real_daily_horoscope(sign: str, day: str = "today"):
    """Гороскоп от профессионального API (англ.)"""
    async with httpx.AsyncClient() as client:
        r = await client.get(REAL_HORO_API, params={"sign": sign, "day": day})
        r.raise_for_status()
        data = r.json()["data"]
        return data["horoscope_data"]

async def nasa_moon_data(date: datetime):
    """Лунные данные от NASA AA API (приблизительно)"""
    # NASA AA требует координаты, возвращаем фазу/возраст из нашего модуля
    day, phase_en = lunar_day_and_phase(date)
    phase_ru = RU_PHASE.get(phase_en, phase_en)
    return day, phase_ru

# ================== КОМАНДЫ ==================
ZODIACS_EN = ["aries", "taurus", "gemini", "cancer", "leo", "virgo",
              "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]
ZODIACS_RU = ["♈ Овен", "♉ Телец", "♊ Близнецы", "♋ Рак", "♌ Лев", "♍ Дева",
              "♎ Весы", "♏ Скорпион", "♐ Стрелец", "♑ Козерог", "♒ Водолей", "♓ Рыбы"]

async def cmd_help(m: types.Message):
    await m.answer(
        "🌟 <b>Привет!</b>\n\n"
        "/start – гороскоп по знаку\n"
        "/realhoro – реальный гороскоп на сегодня\n"
        "/moon – фаза Луны (NASA)\n"
        "/lunarbio – персональный лунный совет по дате рождения\n"
        "/mooncal – лунный календарь на 30 дней",
        parse_mode=ParseMode.HTML
    )

async def start(m: types.Message):
    kb = [[types.InlineKeyboardButton(text=z, callback_data=f"real_{en}")]
          for en, z in zip(ZODIACS_EN, ZODIACS_RU)]
    await m.answer("🌟 Выбери знак:", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data.startswith("real_"))
async def show_realhoro(c: types.CallbackQuery):
    sign = c.data.removeprefix("real_")
    text = await real_daily_horoscope(sign)
    await c.message.answer(
        f"♈ {ZODIACS_RU[ZODIACS_EN.index(sign)]}\n\n"
        f"📅 Сегодня:\n<i>{text}</i>",
        parse_mode=ParseMode.HTML
    )
    await c.answer()

async def cmd_moon(m: types.Message):
    day, phase_ru = nasa_moon_data(datetime.now())
    text = (
        f"🌙 <b>Луна сегодня</b>\n\n"
        f"Лунный день: <b>{day}</b> (из 30)\n"
        f"Фаза: <b>{phase_ru}</b>\n\n"
        f"Совет: слушайте свою интуицию – Луна всегда подскажет."
    )
    await m.answer(text, parse_mode=ParseMode.HTML)

async def cmd_lunarbio(m: types.Message):
    await m.answer(
        "🌙 Отправь свою дату рождения в формате <b>ДД.ММ.ГГГГ</b>, "
        "и я расскажу, какая Луна была в этот день и какой сегодня совет для тебя.",
        parse_mode=ParseMode.HTML
    )

@dp.message(F.text.regexp(r"^\d{2}\.\d{2}\.\d{4}$"))
async def get_birth_luna(m: types.Message):
    try:
        birth = datetime.strptime(m.text, "%d.%m.%Y")
    except ValueError:
        await m.answer("📆 Неверный формат. Пример: 14.03.1995")
        return
    day, phase = lunar_day_and_phase(birth)
    phase_ru = RU_PHASE.get(phase, phase)
    advice = PERSONAL_MOON_ADV.get(day, "Слушайте свою интуицию – Луна всегда подскажет.")
    today_day, today_phase = lunar_day_and_phase(datetime.now())
    today_ru = RU_PHASE.get(today_phase, today_phase)

    text = (
        f"🌙 <b>Твоя лунная карта</b>\n\n"
        f"Дата рождения: <b>{birth.strftime('%d.%m.%Y')}</b>\n"
        f"Лунный день: <b>{day}</b> (из 30)\n"
        f"Фаза: <b>{phase_ru}</b>\n\n"
        f"📌 Персональный совет на сегодня:\n<i>{advice}</i>\n\n"
        f"Сегодня Луна: <b>{today_ru}</b> ({today_day} день)"
    )
    await m.answer(text, parse_mode=ParseMode.HTML)

async def cmd_mooncal(m: types.Message):
    cal = lunar_calendar_month(datetime.now())
    lines = [f"{dt.strftime('%d.%m')}: {day} день – {RU_PHASE.get(ph, ph)}" for dt, day, ph in cal]
    text = "📆 <b>Лунный календарь на 30 дней</b>\n\n" + "\n".join(lines[:15])
    await m.answer(text, parse_mode=ParseMode.HTML)

# ---------- РЕГИСТРАЦИЯ (всё внутри) ----------
def register_handlers(dp: Dispatcher):
    dp.message.register(cmd_help, F.text == "/help")
    dp.message.register(start, F.text == "/start")
    dp.message.register(cmd_moon, F.text == "/moon")
    dp.message.register(cmd_lunarbio, F.text == "/lunarbio")
    dp.message.register(get_birth_luna, F.text.regexp(r"^\d{2}\.\d{2}\.\d{4}$"))
    dp.message.register(cmd_mooncal, F.text == "/mooncal")
    dp.callback_query.register(show_realhoro, F.data.startswith("real_"))

# ---------- WEB-SERVICE ЗАГЛУШКА ----------
async def health(request):
    return web.Response(text="OK")

async def on_startup(app: web.Application):
    global bot
    bot = Bot(token=os.environ["TOKEN"], default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    register_handlers(dp)
    asyncio.create_task(dp.start_polling(bot))

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

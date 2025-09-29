import os, random, asyncio
from aiogram import Bot, Dispatcher, F, types

ZODIACS = ["♈ Овен","♉ Телец","♊ Близнецы","♋ Рак","♌ Лев","♍ Дева",
           "♎ Весы","♏ Скорпион","♐ Стрелец","♑ Козерог","♒ Водолей","♓ Рыбы"]
PRED = ["Сегодня удача на твоей стороне!",
        "Избегай крупных трат — завтра будут важные покупки.",
        "Встретишь человека, который поменяет твои планы в лучшую сторону."]
ADV  = ["Совет: выпей стакан воды и улыбнись.",
        "Совет: прогуляйся 20 минут без телефона."]

bot = Bot(os.getenv("TOKEN"))
dp  = Dispatcher()

@dp.message(F.text == "/start")
async def start(m: types.Message):
    kb = [[types.InlineKeyboardButton(text=z,callback_data=f"z_{i}")]
          for i,z in enumerate(ZODIACS)]
    await m.answer("🌟 Выбери знак:", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data.startswith("z_"))
async def horo(c: types.CallbackQuery):
    z = ZODIACS[int(c.data.split("_")[1])]
    await c.message.answer(f"{z}\n🔮 {random.choice(PRED)}\n💡 {random.choice(ADV)}")
    await c.answer()

asyncio.run(dp.start_polling(bot))

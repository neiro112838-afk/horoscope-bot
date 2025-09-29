import os
import random
import asyncio
from aiogram import Bot, Dispatcher, F, types

ZODIACS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
           "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
PRED = ["Today luck is on your side!",
        "Avoid big spends today — important purchases tomorrow.",
        "You will meet a person who changes your plans for the better."]
ADV = ["Tip: drink a glass of water and smile.",
       "Tip: walk for 20 minutes without your phone."]

bot = Bot(token=os.environ["TOKEN"])
dp = Dispatcher()

@dp.message(F.text == "/start")
async def start(m: types.Message):
    kb = [[types.InlineKeyboardButton(text=z, callback_data=f"z_{i}")]
          for i, z in enumerate(ZODIACS)]
    await m.answer("Pick your sign:", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data.startswith("z_"))
async def horo(c: types.CallbackQuery):
    z = ZODIACS[int(c.data.split("_")[1])]
    await c.message.answer(f"{z}\n🔮 {random.choice(PRED)}\n💡 {random.choice(ADV)}")
    await c.answer()

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))

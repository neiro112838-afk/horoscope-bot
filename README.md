# Real-Horoscope-Telegram-Bot

**Русскоязычный Telegram-бот**, который:
- выдаёт **реальные гороскопы** (профессиональное API)  
- показывает **фазу Луны по данным NASA**  
- строит **натальную карту** и **лунный календарь**  
- работает **24/7** в облаке Render

## Как запустить
1. Создайте бота у [@BotFather](https://t.me/BotFather), получите токен
2. Создайте **Web-Service** на [render.com](https://render.com):
   - Repository: ваш GitHub-репозиторий  
   - Build Command: `pip install -r requirements.txt`  
   - Start Command: `python bot.py`  
   - Environment Variables:  
     - `TOKEN` = токен от BotFather  
     - `PORT` = 8080  
3. Добавьте команды в меню бота:

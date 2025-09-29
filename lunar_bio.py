"""
Полноценный модуль «Персональные лунные рекомендации»
Подключается: from lunar_bio import setup_lunar_bio, PERSONAL_MOON_ADV
"""
from datetime import datetime, timedelta
from typing import List, Tuple
import math

# -------------------- астрономические константы --------------------
SYNODIC_MONTH = 29.53058867          # средний синодический месяц
KNOWN_NEW_MOON = datetime(2000, 1, 6, 18, 14)  # эфемерида NASA

# -------------------- публичные: советы по лунному дню --------------------
PERSONAL_MOON_ADV = {
    1:  "Сегодня отличный день для новых начинаний – вы родились в день новой Луны.",
    2:  "Действуйте спокойно, нарабатывайте ресурс – вы «растущая» Луна.",
    3:  "Доводите дела до середины – вы «первая четверть».",
    4:  "Расширяйте горизонты, учитесь – вы «растущая» Луна.",
    5:  "Делитесь знаниями – вы «полная» Луна.",
    6:  "Избавляйтесь от лишнего – вы «убывающая» Луна.",
    7:  "Подводите итоги, отдыхайте – вы «последняя четверть».",
    8:  "Слушайте интуицию – вы «убывающая» Луна.",
    9:  "Планируйте, но не спешите – вы «новолуние».",
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

# -------------------- расчёты --------------------
def moon_age(dt: datetime) -> float:
    """Возраст Луны в днях (0-29.5) от последнего новолуния."""
    delta = dt - KNOWN_NEW_MOON
    return (delta.total_seconds() / 86400) % SYNODIC_MONTH

def lunar_day_and_phase(dt: datetime) -> Tuple[int, str]:
    age = moon_age(dt)
    day = int(age) + 1                       # 1-30
    phase = _phase_name(age)
    return day, phase

def _phase_name(age: float) -> str:
    if age < 1.845:    return "New"
    if age < 5.53:     return "Waxing Crescent"
    if age < 9.22:     return "First Quarter"
    if age < 12.91:    return "Waxing Gibbous"
    if age < 16.59:    return "Full"
    if age < 20.27:    return "Waning Gibbous"
    if age < 23.95:    return "Last Quarter"
    return "Waning Crescent"

# -------------------- публичные функции --------------------
def get_today_lunar() -> Tuple[int, str]:
    return lunar_day_and_phase(datetime.now())

def get_birth_lunar(birth: datetime) -> Tuple[int, str]:
    return lunar_day_and_phase(birth)

def personal_today_advice(birth_date: datetime) -> str:
    day, _ = get_birth_lunar(birth_date)
    return PERSONAL_MOON_ADV.get(day, "Слушай свою интуицию – Луна всегда подскажет.")

def lunar_calendar_month(start: datetime) -> List[Tuple[datetime, int, str]]:
    """Возвращает список (дата, лунный_день, фаза) на 30 дней от start."""
    cal = []
    for d in range(30):
        dt = start + timedelta(days=d)
        day, phase = lunar_day_and_phase(dt)
        cal.append((dt, day, phase))
    return cal

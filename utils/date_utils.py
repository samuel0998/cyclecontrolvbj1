import pytz
from datetime import datetime, timedelta
from config import Config


def get_current_cycle_window():
    tz = pytz.timezone(Config.TIMEZONE)
    now = datetime.now(tz)

    hour = 7 if now.hour < 19 else 19
    start = now.replace(hour=hour, minute=0, second=0, microsecond=0)

    if now.hour < 7:
        start -= timedelta(days=1)

    end = start + timedelta(hours=12)

    return start, end

from datetime import datetime


def calculate_time_left(expires_at_iso):
    """
    Retorna tempo restante em segundos
    """
    expires_at = datetime.fromisoformat(expires_at_iso)
    now = datetime.utcnow()

    seconds = int((expires_at - now).total_seconds())

    return max(seconds, 0)

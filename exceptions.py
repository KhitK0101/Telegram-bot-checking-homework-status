
class WrongResponseCode(Exception):
    """Неверный ответ API."""
    pass


class TelegramError(Exception):
    """Ошибка отправки сообщения в telegram."""
    pass


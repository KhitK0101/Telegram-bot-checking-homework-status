
class WrongResponseCode(Exception):
    pass


class NotForSend(Exception):
    pass


class EmptyAPI(NotForSend):
    pass


class TelegramError(NotForSend):
    pass
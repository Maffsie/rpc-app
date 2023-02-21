from telegram import Bot

from RPC.helper import Configurable, WithLogging


class TBot(Configurable, WithLogging):
    app_config = {
        "telegram_botkey": str,
    }
    errnos = {
        "TELEGRAM_BOTKEY": "FTGBKA",
    }
    errdes = {"FTGBKA": "No bot key present for Telegram!"}
    api: Bot

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api = Bot(token=self.app_config.get("telegram_botkey"))


s_cls = TBot

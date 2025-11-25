"""
Конфигурационный файл для Telegram бота займов
"""

import os
from dataclasses import dataclass


@dataclass
class BotConfig:
    """Конфигурация бота"""
    # Токен бота (получите у @BotFather)
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

    # Настройки прокси
    USE_PROXY: bool = False
    PROXY_HOST: str = "213.226.78.86"
    PROXY_PORT: int = 8000
    PROXY_USERNAME: str = "E5XeXW"
    PROXY_PASSWORD: str = "PcnzYp"
    PROXY_TYPE: str = "socks5"  # socks5 или http

    @property
    def proxy_url(self) -> str:
        """Возвращает URL прокси"""
        return f"{self.PROXY_TYPE}://{self.PROXY_USERNAME}:{self.PROXY_PASSWORD}@{self.PROXY_HOST}:{self.PROXY_PORT}"


# Создаем экземпляр конфигурации
config = BotConfig()

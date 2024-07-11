from telegram_bot import startup
import asyncio
from loguru import logger

logger.add("logs/pnopbot.log", rotation="1 day")


def main():
    try:
        asyncio.run(startup())
    except KeyboardInterrupt:
        logger.info("Работа программы завершена")


if __name__ == '__main__':
    main()

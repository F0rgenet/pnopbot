import asyncio
import os

from aiogram import Bot
from dotenv import load_dotenv


def main():
    load_dotenv(".env")

    bot_token = os.getenv("TELEGRAM_API_TOKEN")
    bot = Bot(token=bot_token)


if __name__ == '__main__':
    main()

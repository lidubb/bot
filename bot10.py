import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("bot")

TOKEN = os.getenv("BOT_TOKEN")
SECRET = os.getenv("WEBHOOK_SECRET", "change_me_secret")
# Render сам задаёт RENDER_EXTERNAL_URL, на других платформах укажите BASE_URL
BASE_URL = os.getenv("BASE_URL") or os.getenv("RENDER_EXTERNAL_URL")
PORT = int(os.getenv("PORT", "8080"))
WEBHOOK_PATH = "/webhook"

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    log.info("start from user_id=%s", message.from_user.id)
    await message.answer(f"Привет, {message.from_user.first_name}! Я работаю в облаке.")


@dp.message(lambda m: m.text)
async def echo(message: types.Message):
    log.info("message from user_id=%s", message.from_user.id)
    await message.answer(message.text)


async def on_startup(bot: Bot):
    url = f"{BASE_URL}{WEBHOOK_PATH}"
    await bot.set_webhook(url, secret_token=SECRET, drop_pending_updates=True)
    log.info("Webhook установлен: %s", url)


async def on_shutdown(bot: Bot):
    await bot.delete_webhook()
    log.info("Webhook удалён")


async def health(request):
    return web.Response(text="OK")


def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()
    app.router.add_get("/", health)  # для проверки доступности
    SimpleRequestHandler(dp, bot, secret_token=SECRET).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    main()
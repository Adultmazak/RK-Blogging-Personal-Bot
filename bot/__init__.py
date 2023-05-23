import logging
import logging.config
import os
from pyrogram import Client
from aiohttp import web
from bot.config import Config


# Get logging configurations

logging.getLogger().setLevel(logging.INFO)

PORT = int(os.environ.get('PORT', '80'))


class Bot(Client):
    def __init__(self):
        super().__init__(
            Config.BOT_USERNAME,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins=dict(root="bot/plugins"),
        )

    async def start(self):

        await super().start()

        me = await self.get_me()
        self.owner = await self.get_users(int(Config.OWNER_ID))
        self.username = f"@{me.username}"

        logging.info("Bot started")

        download_folder = "downloads"

        if not os.path.exists(download_folder):
            os.makedirs(download_folder)

        if Config.WEB_SERVER:
            routes = web.RouteTableDef()

            @routes.get("/", allow_head=True)
            async def root_route_handler(request):
                res = {
                    "status": "running",
                }
                return web.json_response(res)

            async def web_server():
                web_app = web.Application(client_max_size=30000000)
                web_app.add_routes(routes)
                return web_app

            app = web.AppRunner(await web_server())
            await app.setup()
            await web.TCPSite(app, "0.0.0.0", PORT).start()

    async def stop(self, *args):
        await super().stop()

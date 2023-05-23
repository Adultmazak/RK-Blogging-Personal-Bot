import time
from bot.config import Config
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from pytz import timezone


def current_ist_time():
    return datetime.now(timezone('Asia/Kolkata'))


class Database:
    def __init__(self, uri, database_name):
        self._client = AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.users = self.db["users"]
        self.misc = self.db["misc"]

    async def get_db_size(self):
        return (await self.db.command("dbstats"))["dataSize"]

    async def get_bot_config(self):
        return await self.misc.find_one({"bot": Config.BOT_USERNAME})

    async def create_config(self):
        await self.misc.insert_one(
            {
                "bot": Config.BOT_USERNAME,
            }
        )

    async def update_stats(self, value):
        myquery = {
            "bot": Config.BOT_USERNAME,
        }
        newvalues = {
            "$set": value
        }
        return await self.misc.update_one(myquery, newvalues)

    async def get_user(self, user_id):
        user_id = int(user_id)
        user = await self.users.find_one({"user_id": user_id})
        if not user:
            res = {
                "user_id": user_id,
                "banned": False,
                "blogger_ids": [],
                "default_blog": 0,  # blog id
                "last_verified": datetime(1970, 1, 1),
                "access_days": 0,  # in seconds,
                "auto_title": False,
                "auto_post": False,
                "auto_bold": False,
            }
            await self.users.insert_one(res)
            user = await self.users.find_one({"user_id": user_id})
        return user

    async def update_user(self, user_id, value, tag="set"):
        user_id = int(user_id)
        myquery = {
            "user_id": user_id,
        }
        newvalues = {f"${tag}": value}
        return await self.users.update_one(myquery, newvalues)

    async def filter_users(self):
        return self.users.find({})

    async def filter_user_by_value(self, value):
        return await self.users.find_one(value)

    async def total_users_count(self, ):
        return await self.users.count_documents({})

    async def get_all_users(self, ):
        return self.users.find({})

    async def delete_user(self, user_id):
        await self.users.delete_one({"user_id": int(user_id)})

    async def is_user_exist(self, id):
        user = await self.users.find_one({"user_id": int(id)})
        return bool(user)

    async def update_user_blog(self, user_id, blog_id, tag="push"):
        user_id = int(user_id)
        myquery = {
            "user_id": user_id,
        }
        newvalues = {f"${tag}": {"blogger_ids": blog_id}}
        return await self.users.update_one(myquery, newvalues)


db = Database(Config.DATABASE_URL, Config.DATABASE_NAME)

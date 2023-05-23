import os
from dotenv import load_dotenv
from pyrogram.types import InlineKeyboardButton as button, InlineKeyboardMarkup as markup

load_dotenv()


def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default


class Config(object):

    BOT_USERNAME = os.environ.get("BOT_USERNAME")
    API_ID = int(os.environ.get("API_ID"))

    API_HASH = os.environ.get("API_HASH")
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    ADMINS = (
        [int(i.strip()) for i in os.environ.get("ADMINS").split(",")]
        if os.environ.get("ADMINS")
        else []
    )
    DATABASE_NAME = os.environ.get("DATABASE_NAME", BOT_USERNAME)
    DATABASE_URL = os.environ.get("DATABASE_URL", None)
    OWNER_ID = int(os.environ.get("OWNER_ID"))
    ADMINS.append(OWNER_ID) if OWNER_ID not in ADMINS else []

    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "0"))
    UPDATE_CHANNEL = int(os.environ.get("UPDATE_CHANNEL", ""))
    BROADCAST_AS_COPY = is_enabled(
        (os.environ.get("BROADCAST_AS_COPY", "False")), False
    )
    OWNER_USERNAME = os.environ.get("OWNER_USERNAME", None)
    WEB_SERVER = is_enabled(os.environ.get("WEB_SERVER", "False"), False)

    BLOG_ID = os.environ.get("BLOG_ID", "")
    BLOGGER_EMAIL = os.environ.get("BLOGGER_EMAIL")

    WATERMARK_LOCATION = os.environ.get("WATERMARK_LOCATION", "images/watermark.png")


class Script(object):
    start_message = "Welcome to the Telegram bot that helps you post on Blogger! With our bot, you can set a default site to post to instantly or add tags to post to specific sites. You can also turn on or off the instant posting feature and auto title feature. you can even write or ask the bot to write a post for you, attach images, and add YouTube videos to your posts. Let's get started!"
    START_MESSAGE = os.environ.get("START_MESSAGE", start_message)

    help_message = "To use Your Telegram bot, you can follow these commands:\n\n/settings"
    HELP_MESSAGE = os.environ.get("HELP_MESSAGE", help_message)

    about_message = "Our Telegram bot is a platform that makes it easier for you to post on Blogger. Whether you have a post ready to go, we've got you covered. With our bot, you can set a default site to post to, add tags to post to specific sites, and even turn on or off the instant posting and auto title features. Get started with our awesome Bot Today!"
    ABOUT_MESSAGE = os.environ.get("ABOUT_MESSAGE", about_message)

    MY_BLOG_TEXT = "**Title:** {title}\n**Description:** {description}\n**URL:** {url}\n**Total posts:** {total_posts}\n**Default Blog:** {default_blog}"
    POST_VIEW_TEXT = "**Title:** {title}\n**URL:** {url}\n**Published at:** {published}\n**Last updated at:** {updated}\n**Author:** {author}\n"

    LOADING_TEXT = "Hold on a sec..."


class InlineButtons(object):
    START_BUTTON = markup(
        [
            [
                button("My Blogs", callback_data="my_blog"),
                button("Help ❓", callback_data="help"),
            ],
            [
                button("Settings ⚙️", callback_data="settings"),
                button("My Plan 📈", callback_data="my_plan"),
            ],
            [
                button("New Post 💻", callback_data="new_post"),
                button("About 🧲", callback_data="about"),
            ],
            [
                button("Add new blog ➕", callback_data="auth"),
            ]
        ]
    )

    HOME_BUTTON = markup(
        [
            [button("🏠 Home", callback_data="start")]
        ]
    )

    AUTH_BUTTON = markup(
        [
            [button("Connect your Blog 🔗", callback_data="auth")],

            [
                button("Help ❓", callback_data="help"),
                button("About 🧲", callback_data="about"),
            ]
        ]
    )


import json
import traceback

from googleapiclient.errors import HttpError
from pyrogram import Client, filters, types
from pyrogram.types import InlineKeyboardButton as button
from pyrogram.types import InlineKeyboardMarkup as markup

from blogger import blogger
from bot.config import Config, Script
from bot.database import db
from bot.utils import get_labels, get_post_details, make_post, temp


@Client.on_message(filters.private & (filters.photo | filters.text | filters.document) & filters.incoming & filters.user(Config.ADMINS))
async def upload_post(c: Client, m: types.Message):


    document = m.document
    if document and not document.mime_type.startswith("image/"):
        return

    image = m.photo

    user_id = m.from_user.id
    user = await db.get_user(user_id)
    blog_id = user["default_blog"]

    if not user["blogger_ids"]:
        return await m.reply("Add any new blog for uploading post")

    if not blog_id:
        return await m.reply("Set your default blog website")

    if user["auto_post"]:
        delete = await m.reply(Script.LOADING_TEXT)
        try:
            title, caption, image = await make_post(m)
            labels = await get_labels(caption, blog_id)
            blog_post = await blogger.create_post(blog_id, title, caption, image, labels)

        except HttpError as error:
            error_message = error.content.decode('utf-8')
            error_json = json.loads(error_message)
            error_reason = error_json['error']['errors'][0]['reason']
            if error_reason == "rateLimitExceeded":
                await m.reply("Rate limit exceeded, try again later")
                return
            return await m.reply(f"Error: {error_reason}")

        except Exception as e:
            traceback.print_exc()
            await m.reply("Some error occured, Try Again Later...")
            return

        finally:
            await delete.delete()

        text, btn = await get_post_details(blog_id, blog_post["id"])

        await m.reply(text, disable_web_page_preview=1, reply_markup=btn)
        return

    elif not user["auto_title"]:
        temp.convs[user_id] = "asked_title"
        temp.infos[user_id] = {"message_id": m.id}
        await m.reply("Send me the title for this post", quote=1, reply_markup=markup([[button("Cancel the process", "cancel",)]]))
    else:
        btn = [
            [
                button("Confirm", callback_data=f"cp#{m.id}"),
                button("Cancel", callback_data="delete"),
            ],
        ]
        edit = await m.copy(m.from_user.id,)
        await edit.reply("Are you sure you want to post this post?", disable_web_page_preview=1, reply_markup=markup(btn), quote=1)

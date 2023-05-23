
import contextlib
import json
import os
import re
import traceback

from googleapiclient.errors import HttpError
from pyrogram import Client, filters, types
from pyrogram.types import InlineKeyboardButton as button
from pyrogram.types import InlineKeyboardMarkup as markup

from blogger import blogger
from bot.config import Config, InlineButtons, Script
from bot.database import db
from bot.utils import (add_user, extract_link, get_conv, get_labels,
                       get_post_details, get_user_info_text, get_user_setting,
                       is_blogger_site, make_post, temp)


@Client.on_callback_query(filters.regex("start"))
@Client.on_message(filters.command("start") & filters.private & filters.incoming & filters.user(Config.ADMINS))
async def start(c: Client, m: types.Message | types.CallbackQuery):
    await add_user(c, m)
    user_id = m.from_user.id
    if isinstance(m, types.CallbackQuery):
        m = m.message
        await m.delete()

    user = await db.get_user(user_id)
    reply_markup = (
        InlineButtons.START_BUTTON
        if user["blogger_ids"]
        else InlineButtons.AUTH_BUTTON
    )
    await m.reply_text(
        Script.START_MESSAGE, disable_web_page_preview=True, reply_markup=reply_markup
    )


@Client.on_callback_query(filters.regex("about"))
@Client.on_message(filters.command("about") & filters.private & filters.incoming & filters.user(Config.ADMINS))
async def about(c: Client, m: types.Message | types.CallbackQuery):
    if isinstance(m, types.CallbackQuery):
        m = m.message
        await m.delete()

    await m.reply_text(
        Script.ABOUT_MESSAGE, disable_web_page_preview=True, reply_markup=InlineButtons.HOME_BUTTON
    )


@Client.on_callback_query(filters.regex("help"))
@Client.on_message(filters.command("help") & filters.private & filters.incoming & filters.user(Config.ADMINS))
async def help(c: Client, m: types.Message | types.CallbackQuery):
    if isinstance(m, types.CallbackQuery):
        m = m.message
        await m.delete()

    await m.reply_text(
        Script.HELP_MESSAGE, disable_web_page_preview=True, reply_markup=InlineButtons.HOME_BUTTON
    )


@Client.on_callback_query(filters.regex("cancel"))
@Client.on_message(filters.command("cancel") & filters.private & filters.incoming & filters.user(Config.ADMINS))
async def cancel(c: Client, m: types.Message | types.CallbackQuery):
    user_id = m.from_user.id
    if isinstance(m, types.CallbackQuery):
        m = m.message
        await m.delete()

    if user_id in temp.convs:
        del temp.convs[user_id]
        del temp.infos[user_id]
        await m.reply_text("Cancelled", disable_web_page_preview=1, quote=1)
    else:
        await m.reply_text("No active process", disable_web_page_preview=1, quote=1)


@Client.on_callback_query(filters.regex("auth"))
@Client.on_message(filters.command("auth") & filters.private & filters.incoming & filters.user(Config.ADMINS))
async def auth(c: Client, m: types.Message | types.CallbackQuery):
    user_id = m.from_user.id
    if isinstance(m, types.CallbackQuery):
        m = m.message
        await m.delete()

    text = "Send your blogger website URL"
    temp.convs[user_id] = "asked_url"
    temp.infos[user_id] = {}

    await m.reply_text(
        text, disable_web_page_preview=True, quote=1, reply_markup=markup([[button("Cancel the process", "cancel",)]])
    )


@Client.on_message(filters.private & get_conv("asked_url") & filters.incoming & filters.user(Config.ADMINS))
async def url_handler(_, m: types.Message):
    url = m.text.lower()
    user_id = m.from_user.id

    links = await extract_link(url)
    if not links:
        return await m.reply_text("Not a valid url")

    is_valid_url = await is_blogger_site(links[0])
    if not is_valid_url:
        return await m.reply_text("Not a valid blogger website")

    user_info = await db.get_user(user_id)
    with contextlib.suppress(Exception):
        if await blogger.get_blog_id(url) in user_info["blogger_ids"]:
            del temp.convs[user_id]
            del temp.infos[user_id]
            return await m.reply_text("This blogger website already exists in your account", reply_markup=InlineButtons.HOME_BUTTON)
    temp.infos[user_id].update({"url": url})

    await m.reply_text("Added your website URL to the database", disable_web_page_preview=True, quote=1)
    await m.reply_text(f"Add {Config.BLOGGER_EMAIL} as a collaborator in your blogger website", disable_web_page_preview=True, quote=1, reply_markup=markup([[button("Added", "added",)]]))


@Client.on_message(filters.private & get_conv("asked_title") & filters.incoming & filters.user(Config.ADMINS))
async def asked_title(c: Client, m: types.Message):

    delete = await m.reply(Script.LOADING_TEXT)
    title = m.text
    user_id = m.from_user.id
    user_info = temp.infos.get(m.from_user.id)
    post = await c.get_messages(user_id, user_info["message_id"])
    if not m.text:
        await delete.delete()
        await m.reply("Send me the title for this post", reply_to_message_id=user_info["message_id"])
        return

    user = await db.get_user(user_id)
    blog_id = user["default_blog"]
    try:
        _, caption, image = await make_post(post)
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

    except Exception:
        traceback.print_exc()
        await m.reply("Some error occured, Try Again Later...")
        return

    finally:
        await delete.delete()

    text, btn = await get_post_details(blog_id, blog_post["id"])

    await m.reply(text, disable_web_page_preview=1, reply_markup=btn)

    await delete.delete()

    with contextlib.suppress(KeyError):
        del temp.convs[user_id]

    with contextlib.suppress(KeyError):
        del temp.infos[user_id]


@Client.on_callback_query(filters.regex("my_blog"))
@Client.on_message(filters.command("my_blog") & filters.private & filters.incoming & filters.user(Config.ADMINS))
async def my_blog(c: Client, m: types.Message | types.CallbackQuery):
    user_id = m.from_user.id
    if isinstance(m, types.CallbackQuery):
        m = m.message
        await m.delete()

    user_info = await db.get_user(user_id)

    if not user_info["blogger_ids"]:
        return await m.reply_text("No blogger websites were found")

    btn = [[button("Manage your blogs 👇", callback_data="ident")]]

    for blog_id in user_info["blogger_ids"]:
        title = await blogger.get_title(blog_id)
        btn.append([
            button(f"Blog Name: {title}",
                   callback_data=f"view_blog#{blog_id}"),
        ])

    btn.append([button("🏠 Home", callback_data="start")])

    await m.reply("Here are your blogs, you can edit by clicking on the Edit button below", reply_markup=markup(btn))


@Client.on_callback_query(filters.regex("settings"))
@Client.on_message(filters.command("settings") & filters.private & filters.incoming & filters.user(Config.ADMINS))
async def settings(c: Client, m: types.Message | types.CallbackQuery):
    user_id = m.from_user.id
    if isinstance(m, types.CallbackQuery):
        m = m.message
        await m.delete()
    reply_markup = await get_user_setting(user_id)
    user_info = await db.get_user(user_id)
    blog_url = await blogger.get_blog_address(
        user_info["default_blog"]) if user_info["default_blog"] else None
    await m.reply(f"You settings\nDefault Blog: {blog_url}", reply_markup=reply_markup)


@Client.on_callback_query(filters.regex("^setgs"))
async def user_setting_cb(c, query: types.CallbackQuery):
    _, setting, toggle, user_id = query.data.split("#")
    myvalues = {setting: toggle == "True"}
    await db.update_user(user_id, myvalues)
    reply_markup = await get_user_setting(user_id)
    try:
        await query.message.edit_reply_markup(reply_markup)
        setting = re.sub("is|_", " ", setting).title()
        toggle = "Enabled" if toggle == "True" else "Disabled"
        await query.answer(f"{setting} {toggle} Successfully", show_alert=True)
    except Exception as e:
        print("Error occurred while updating user information")


@Client.on_callback_query(filters.regex("my_plan"))
@Client.on_message(filters.command("myplan") & filters.private & filters.incoming & filters.user(Config.ADMINS))
async def my_plan(c: Client, m: types.Message | types.CallbackQuery):
    og_user_id = m.from_user.id
    if isinstance(m, types.CallbackQuery):
        m = m.message
        await m.delete()
    text = await get_user_info_text(og_user_id)
    await m.reply(text)


@Client.on_message(filters.command("watermark") & filters.private & filters.incoming & filters.user(Config.ADMINS))
async def watermark(c: Client, m: types.Message):

    if not m.reply_to_message:
        if os.path.isfile(Config.WATERMARK_LOCATION):
            await c.send_document(m.from_user.id, Config.WATERMARK_LOCATION, caption="Reply /watermark to any image document")
        else:
            await c.send_message(m.from_user.id, text="No watermark found, Reply /watermark to any image document")
        return 
    
    if m.reply_to_message.document and not m.reply_to_message.document.mime_type.startswith("image/"):
        return await m.reply("Not a proper image, reply to any image document")

    if m.reply_to_message and m.reply_to_message.document:
        await m.reply_to_message.download(Config.WATERMARK_LOCATION)
        await m.reply("Watermark saved")
    else:
        await m.reply("Not a proper image, reply to any image document")

    return


@Client.on_message(filters.command("remove_watermark") & filters.private & filters.incoming & filters.user(Config.ADMINS))
async def remove_watermark(c: Client, m: types.Message):
    if os.path.isfile(Config.WATERMARK_LOCATION):
        os.remove(Config.WATERMARK_LOCATION)
        await m.reply("Watermark removed")
    else:
        await m.reply("Watermark does not exist")
    return
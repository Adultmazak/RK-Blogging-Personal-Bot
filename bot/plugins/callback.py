import contextlib
import json
import math
import traceback

from googleapiclient.errors import HttpError
from pyrogram import Client, filters, types
from pyrogram.types import InlineKeyboardButton as button
from pyrogram.types import InlineKeyboardMarkup as markup

from blogger import blogger
from bot.config import Config, InlineButtons, Script
from bot.database.users_db import db
from bot.utils import (extract_link, get_labels, get_post_details, make_post,
                       temp)


@Client.on_callback_query(filters.regex("added"))
async def add(c: Client, m: types.CallbackQuery):
    user_id = m.from_user.id

    url = temp.infos.get(user_id)

    try:
        blog_id = await blogger.get_blog_id(url['url'])
        is_already_exists = await db.filter_user_by_value({"blog_ids": blog_id})
        if is_already_exists:
            await m.message.edit(
                "This website already exists means this site has been added by someone else already",
                reply_markup=InlineButtons.HOME_BUTTON,
            )
            return
    except Exception as e:
        print(e)

    text = "Your website has been added and will be verified by admin. Once the admin verifies this website, you can able to post your content to this website from this bot.\n\nYou will be notified when the website is ready."

    await m.message.edit(text, reply_markup=InlineButtons.HOME_BUTTON)

    if user_id in temp.convs:
        del temp.convs[user_id]

    if user_id in temp.infos:
        del temp.infos[user_id]

    mention = m.from_user.mention
    user_id = m.from_user.id

    reply_markup = markup(
        [
            [button("Verify Website", callback_data=f"verify#{user_id}")],
            [
                button(
                    "Not added as collaborator yet", callback_data=f"nocollab#{user_id}"
                ),
            ],
            [
                button("Deny Request", callback_data=f"deny#{user_id}"),
            ],
        ]
    )

    bin_text = f"URL: {url['url']}\n\n{mention} has added this website to the bot. Verify if you have received any invites from this website owner for a collaborator\n\n#CollabRequest"
    await c.send_message(Config.OWNER_ID, bin_text, reply_markup=reply_markup)


@Client.on_callback_query(filters.regex("verify"))
async def verify(c: Client, m: types.CallbackQuery):
    _, user_id = m.data.split("#")
    user_id = int(user_id)
    url = (await extract_link(m.message.text))[0]
    blog_id = await blogger.get_blog_id(url)
    await db.update_user_blog(user_id, blog_id)
    user_info = await db.get_user(user_id)
    if not user_info["default_blog"]:
        await db.update_user(user_id, {"default_blog": blog_id})

    await c.send_message(
        user_id,
        f"Your website: {url}\nAdded successfully. /my_blog for more information",
        reply_markup=InlineButtons.HOME_BUTTON,
    )
    await m.message.edit("User has been notified")


@Client.on_callback_query(filters.regex("deny"))
async def deny(c: Client, m: types.CallbackQuery):
    _, user_id = m.data.split("#")
    user_id = int(user_id)
    mention = (await c.get_users(Config.OWNER_ID)).mention
    url = (await extract_link(m.message.text))[0]
    text = f"Unfortunately, this [website]({url}) has been denied by the administrator, Contact the [administrator]({mention}) for more details.\nYou can try adding some other website"
    await c.send_message(user_id, text, reply_markup=InlineButtons.HOME_BUTTON)
    await m.message.edit("Website has been denied")


@Client.on_callback_query(filters.regex("new_post"))
async def new_post(c: Client, m: types.CallbackQuery):
    await m.answer("Just forward any text or image post", show_alert=1)
    return


@Client.on_callback_query(filters.regex("nocollab"))
async def nocollab(c: Client, m: types.CallbackQuery):
    _, user_id = m.data.split("#")
    user_id = int(user_id)
    mention = (await c.get_users(Config.OWNER_ID)).mention
    url = (await extract_link(m.message.text))[0]
    text = f"Website: {url}\n\nWe reviewed your request, as far our information, you have not added {Config.BLOGGER_EMAIL} as a collaborator to your website. Please add and re confirm once by clicking the below button or Contact {mention} for more information"
    await c.send_message(
        user_id,
        text,
        reply_markup=markup(
            [
                [
                    button(
                        "Added",
                        "added",
                    )
                ]
            ]
        ),
    )
    await m.message.edit("User has been notified")
    temp.infos = {user_id: {"url": url}}


@Client.on_callback_query(filters.regex("^view_blog"))
async def view_blog(c: Client, m: types.CallbackQuery):
    user_id = m.from_user.id
    user_info = await db.get_user(user_id)

    _, blog_id = m.data.split("#")

    if blog_id not in user_info["blogger_ids"]:
        await m.answer("This blog is not available", show_alert=1)
        await m.delete()
        return

    default_blog = user_info["default_blog"] == blog_id

    blog_info = await blogger.get_blogger_info(blog_id)
    text = Script.MY_BLOG_TEXT.format(
        title=blog_info["name"],
        description=blog_info["description"],
        url=blog_info["url"],
        total_posts=blog_info["posts"]["totalItems"],
        default_blog=default_blog,
    )

    btn = [
        [
            button("📄 View Blog", url=blog_info["url"]),
            button("🗑️ Remove Blog", callback_data=f"remove_blog#{blog_id}"),
        ],
        [
            button("View Blog Posts",
                   callback_data=f"blog_posts#{blog_id}#None#1"),
        ],
    ]

    None if default_blog else btn.append(
        [
            button(
                "Make this blog deafult",
                callback_data=f"make_default#{blog_id}",
            )
        ]
    )
    btn.append([button("Back", callback_data="my_blog")])

    await m.message.edit(text, reply_markup=markup(btn))


@Client.on_callback_query(filters.regex("make_default"))
async def make_default(c: Client, m: types.CallbackQuery):
    user_id = m.from_user.id
    user_info = await db.get_user(user_id)

    _, blog_id = m.data.split("#")

    if blog_id not in user_info["blogger_ids"]:
        await m.answer("This blog is not available", show_alert=1)
        await m.delete()
        return

    if user_info["default_blog"] == blog_id:
        await m.answer("Already the default blog", show_alert=1)
        return

    await db.update_user(user_id, {"default_blog": blog_id})
    await m.answer(
        "This blog is now the default. Posts will be uploaded in this blog from now",
        show_alert=1,
    )


@Client.on_callback_query(filters.regex("^delete$"))
async def delete(c: Client, m: types.CallbackQuery):
    await m.message.delete()


@Client.on_callback_query(filters.regex("^remove_blog"))
async def remove_blog(c: Client, m: types.CallbackQuery):

    _, blog_id = m.data.split("#")

    btn = [
        [
            button("Confirm", callback_data=f"confirm_remove_blog#{blog_id}"),
            button("Cancel", callback_data="delete"),
        ],
    ]

    text = "Are you sure you want to remove this blog from database? This is not reversible"
    await m.message.edit(text, reply_markup=markup(btn))


@Client.on_callback_query(filters.regex("^confirm_remove_blog"))
async def confirm_remove_blog(c: Client, m: types.CallbackQuery):
    user_id = m.from_user.id

    _, blog_id = m.data.split("#")
    user_info = await db.get_user(user_id)

    if user_info["default_blog"] == blog_id:
        await db.update_user(user_id, {"default_blog": 0})

    await db.update_user_blog(user_id, blog_id, "pull")
    await m.message.edit(
        "Removed blog from database", reply_markup=InlineButtons.HOME_BUTTON
    )


@Client.on_callback_query(filters.regex("blog_posts"))
async def blog_posts(c: Client, m: types.CallbackQuery):
    _, blog_id, page_token, page_no = m.data.split("#")
    page_token = None if page_token == "None" else page_token
    btn = [[button("Manage your Posts 👇", callback_data="ident")]]
    page_no = int(page_no)
    blog_posts, prevPageToken, nextPageToken = await blogger.list_posts(
        blog_id, page_token=None if page_token == 'PAGE1' else page_token)

    if (page_no != 1) and (not temp.tokens.get(page_no - 1)):
        await m.answer("Your clicking one of the old message, make a new request")
        return
    else:
        prevPageToken = temp.tokens.get(page_no-1)

    temp.tokens[page_no] = page_token or "PAGE1"

    blog_info = await blogger.get_blogger_info(blog_id)
    total_posts = int(blog_info["posts"]["totalItems"])
    for post in blog_posts:
        title = post["title"]
        btn.append(
            [
                button(f"Post title: {title}", callback_data="ident"),
                button(
                    "✏️ Edit", callback_data=f"view_posts#{blog_id}#{post['id']}"),
            ]
        )

    if nextPageToken and prevPageToken:
        btn.append(
            [
                button("Previous Page",
                       callback_data=f"blog_posts#{blog_id}#{prevPageToken}#{page_no-1}"),
                button("Next Page",
                       callback_data=f"blog_posts#{blog_id}#{nextPageToken}#{page_no+1}"),

            ]
        )
    elif prevPageToken:
        btn.append(
            [
                button(
                    "Previous Page", callback_data=f"blog_posts#{blog_id}#{prevPageToken}#{page_no-1}"),
            ]
        )

    elif nextPageToken:
        btn.append(
            [
                button(
                    "Next Page", callback_data=f"blog_posts#{blog_id}#{nextPageToken}#{page_no+1}"),
            ]
        )

    btn.append(
        [
            button(f"🗓 {page_no} / {math.ceil(total_posts / 10)}",
                   callback_data="pages"),
        ]
    )

    btn.append([button("🏠 Home", callback_data="start")])

    await m.message.edit(
        "Here are your posts, you can edit by clicking on the Edit button below",
        reply_markup=markup(btn),
    )


@Client.on_callback_query(filters.regex("^view_posts"))
async def view_posts(c: Client, m: types.CallbackQuery):
    _, blog_id, post_id = m.data.split("#")

    post_info = await blogger.get_post(blog_id, post_id)

    text = Script.POST_VIEW_TEXT.format(
        title=post_info["title"],
        url=post_info["url"],
        published=post_info["published"],
        updated=post_info["updated"],
        author=post_info["author"]["displayName"],
    )

    btn = [
        [
            button("📄 View Post", url=post_info["url"]),
            button(
                "🗑️ Remove Post",
                callback_data=f"remove_post#{blog_id}#{post_info['id']}",
            ),
        ],
    ]

    btn.append([button("Back", callback_data="my_blog")])

    await m.message.edit(text, reply_markup=markup(btn), disable_web_page_preview=1)


@Client.on_callback_query(filters.regex("^remove_post"))
async def remove_post(c: Client, m: types.CallbackQuery):

    _, blog_id, post_id = m.data.split("#")

    btn = [
        [
            button("Confirm", callback_data=f"cr_post#{blog_id}#{post_id}"),
            button("Cancel", callback_data="delete"),
        ],
    ]

    text = "Are you sure you want to remove this post from your blog? This is not reversible"
    await m.message.edit(text, reply_markup=markup(btn))


@Client.on_callback_query(filters.regex("cr_post"))
async def confirm_remove_post(c: Client, m: types.CallbackQuery):
    _, blog_id, post_id = m.data.split("#")
    await blogger.delete_post(blog_id, post_id)
    await m.message.edit("Deleted blog", reply_markup=InlineButtons.HOME_BUTTON)


@Client.on_callback_query(filters.regex("^cp#"))
async def confirm_post(c, m: types.CallbackQuery):
    message_id = int(m.data.split('#')[1])
    delete = await m.message.reply(Script.LOADING_TEXT)
    user_id = m.from_user.id
    post = await c.get_messages(user_id, message_id)

    user = await db.get_user(user_id)
    blog_id = user["default_blog"]
    try:
        title, caption, image = await make_post(post)
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
        await m.edit_message_text("Some error occured, Try Again Later...")
        return

    finally:
        await delete.delete()

    text, btn = await get_post_details(blog_id, blog_post["id"])

    await m.edit_message_text(text, disable_web_page_preview=1, reply_markup=btn)

    await delete.delete()

    with contextlib.suppress(KeyError):
        del temp.convs[user_id]

    with contextlib.suppress(KeyError):
        del temp.infos[user_id]

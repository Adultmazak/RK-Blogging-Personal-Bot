import os
import re

import pyimgbox
import requests
from bs4 import BeautifulSoup
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton as button
from pyrogram.types import InlineKeyboardMarkup as markup
from pyrogram.types import Message
from telegraph.aio import Telegraph
from PIL import Image
from blogger import blogger
from bot.config import Config, Script
from bot.database import db

# Create an instance of the Telegraph class
telegraph = Telegraph()


class temp(object):
    convs = {}
    infos = {}
    tokens = {1: "PAGE1"}


def get_conv(level: str):
    async def func(_, __, m):
        return temp.convs.get(m.from_user.id) == level
    return filters.create(func, "ConvHandler")


async def add_user(c, m):
    user_id, mention = m.from_user.id, m.from_user.mention
    is_user = await db.is_user_exist(user_id)

    if not is_user:
        await db.get_user(user_id)


async def is_blogger_site(url):
    response = requests.get(url)
    if "blogger.com" in response.text or "blogspot.com" in response.text:
        return True


async def extract_link(string):
    regex = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
    urls = re.findall(regex, string)
    return ["".join(x) for x in urls]


async def get_user_setting(user_id):
    user = await db.get_user(user_id)
    return markup(
        [
            [
                button("Auto Title", callback_data="ident"),
                button(
                    "❌ Disable" if user["auto_title"] else "✅ Enable",
                    callback_data=f"setgs#auto_title#{not user['auto_title']}#{str(user_id)}",
                ),
            ],
            [
                button("Auto Post", callback_data="ident"),
                button(
                    "❌ Disable" if user["auto_post"] else "✅ Enable",
                    callback_data=f"setgs#auto_post#{not user['auto_post']}#{str(user_id)}",
                ),
            ],
            [
                button("Auto Bold", callback_data="ident"),
                button(
                    "❌ Disable" if user.get("auto_bold") else "✅ Enable",
                    callback_data=f"setgs#auto_bold#{not user.get('auto_bold')}#{str(user_id)}",
                ),
            ],
        ]
    )


async def get_user_info_text(user_id):
    txt = "**User ID:** `{user_id}`\n**Limit:** `{limit} posts per day`"

    return txt.format(
        user_id=user_id,
        limit="Unlimited",
    )


def extract_url(text):
    # Regular expression pattern to match the URL in an HTML hyperlink
    pattern = r'<a href="(https?://\S+)">.*</a>'
    return re.sub(pattern, r'\1', text)


async def format_caption(content, image=None):
    content = content.replace('\n', ' <br>')
    content = extract_url(content)
    links = set(await extract_link(content))

    template = '<a href="{link}"><br><button class="mybutton2"><b>Play Or Download Now</b></button></a>'

    for link in links:
        if is_youtube_url(link):
            hyper_link = replace_youtube_link_with_embed(link)
        else:
            # text = "Click Here" if len(link) > 70 else link
            text = "Play or Download Now"
            hyper_link = template.format(link=link,) #text=text
        content = content.replace(link, hyper_link)

    content = await replace_username(content)
    if image:
        content = f"<img src='{image}' width='100%' height='auto'><br>{content}"
    return content


def replace_youtube_link_with_embed(text):
    youtube_regex = re.compile(
        r"(http(s)?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]*)"
    )

    return youtube_regex.sub(r'<iframe src="https://www.youtube.com/embed/\5" width="100%" height="auto" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>', text)


def is_youtube_url(url):
    regex = r"^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$"
    return re.match(regex, url) != None


async def replace_username(text):
    usernames = re.findall(r"@[A-Za-z0-9_]+", text)
    for old_username in usernames:
        old_username = old_username.replace('@', '')
        text = text.replace(
            f"@{old_username}", f"<a href='https://telegram.dog/{old_username}'>@{old_username}</a>")
    return text


async def make_post(m: Message, html=True):
    caption = m.caption or m.text

    user_id = m.from_user.id

    file_extension = "jpeg"
    if m.document or m.photo:
        file_extension = m.document.mime_type.split("/")[-1] if m.document else file_extension

    image = await m.download(f"downloads/{user_id}_{m.id}.{file_extension}") if m.photo or m.document else None

    water_mark_image = None
    
    if m.document and os.path.isfile(Config.WATERMARK_LOCATION):
        water_mark_image = await add_watermark(image)

    title = caption.split("\n")[0] if caption else None
    uploaded_image = await upload_image(image) if image else None
    uploaded_water_mark_image = await upload_image(water_mark_image) if water_mark_image else None
    os.remove(image) if image is not None else None
    os.remove(water_mark_image) if water_mark_image is not None else None

    if m.document:
        caption = caption.html if html else caption 
        caption = await format_caption(caption)
        caption = f'<img src="{uploaded_water_mark_image}" width="100%" height="auto"><br>{caption}<br><a target="_blank" href="{uploaded_image}" download><br><button class="mybutton2"><b>Download In Full HD</b></button></a>'
    else:
        caption = caption.html if html else caption
        caption = await format_caption(caption, image=uploaded_image)

    soup = BeautifulSoup(caption, 'html.parser')
    fixed_html = str(soup)

    user_info = await db.get_user(user_id)
    bold_css = "font-weight: bold;" if user_info.get("auto_bold") else ""
    centered_html = f"""<div style="text-align: center;{bold_css}">{fixed_html}</div>"""
    return title, centered_html, uploaded_image


async def get_labels(content, blog_id):
    blog_lables = await blogger.get_blog_labels(blog_id)
    return [label for label in blog_lables if label in content]


async def upload_image(image):
    async with pyimgbox.Gallery(title="image") as gallery:
        submission = await gallery.upload(image)
    if submission["success"]:
        return submission["image_url"] 
    else:
        raise Exception(submission["error"])


async def get_post_details(blog_id, post_id, ):
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

    return text, markup(btn)


async def add_watermark(image):
    filename = image.replace(".png", "").replace(".jpg", "").replace(".jpeg", "")
    # Open the image you want to watermark
    image = Image.open(image)
    # Open the PNG watermark image 
    watermark = Image.open(Config.WATERMARK_LOCATION)

    # Get the dimensions of the image and watermark
    image_width, image_height = image.size
    watermark_width, watermark_height = watermark.size

    # Calculate the scale factor to fit the watermark within the image
    scale_factor = min(image_width / watermark_width, image_height / watermark_height)

    # Resize the watermark using the calculated scale factor
    resized_watermark = watermark.resize((int(watermark_width * scale_factor), int(watermark_height * scale_factor)))

    # Calculate the position of the watermark
    pos_x = (image_width - resized_watermark.width) // 2
    pos_y = (image_height - resized_watermark.height) // 2

    # Add the watermark to the image
    image.paste(resized_watermark, (pos_x, pos_y), mask=resized_watermark)

    image_path = f"{filename}_watermark.jpg"
    # Compress the image
    quality = 80  # Adjust this value to set the desired quality
    save_kwargs = {"optimize": True, "quality": quality}
    image.save(image_path, **save_kwargs)

    # Check if the compressed file size is below a threshold
    max_file_size = 200 * 1024  # 100kb
    if os.path.getsize(image_path) > max_file_size:
        # If the file size is above the threshold, keep reducing the quality until it's below the threshold
        while os.path.getsize(image_path) > max_file_size and quality >= 10:
            quality -= 10
            save_kwargs = {"optimize": True, "quality": quality}
            image.save(image_path, **save_kwargs)
    return image_path


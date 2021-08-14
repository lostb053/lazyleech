import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .. import ALL_CHATS
from html_telegraph_poster import TelegraphPoster


async def runcmd(cmd: str) -> Tuple[str, str, int, int]:
    """run command in terminal"""
    args = shlex.split(cmd)
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return (
        stdout.decode("utf-8", "replace").strip(),
        stderr.decode("utf-8", "replace").strip(),
        process.returncode,
        process.pid,
    )

  
def safe_filename(path_):
    if path_ is None:
        return
    safename = path_.replace("'", "").replace('"', "")
    if safename != path_:
        os.rename(path_, safename)
    return safename


def post_to_telegraph(a_title: str, content: str) -> str:
    """Create a Telegram Post using HTML Content"""
    post_client = TelegraphPoster(use_api=True)
    auth_name = "Lazyleech"
    post_client.create_api_token(auth_name)
    post_page = post_client.post(
        title=a_title,
        author=auth_name,
        author_url="https://t.me/lostb053",
        text=content,
    )
    return post_page["url"]


@Client.on_message(filters.command('mediainfo') & filters.chat(ALL_CHATS))
async def mediainfo(client, message):
    reply = message.reply_to_message
    if not reply:
        await message.reply_text("Reply to Media first")
        return
    process = await message.reply_text("<b>Processing..</b>")
    x_media = None
    available_media = (
        "audio",
        "document",
        "photo",
        "sticker",
        "animation",
        "video",
        "voice",
        "video_note",
        "new_chat_photo",
    )
    for kind in available_media:
        x_media = getattr(reply, kind, None)
        if x_media is not None:
            break
    if x_media is None:
       await process.edit_text("Reply To a Valid Media Format")
       return
    media_type = str(type(x_media)).split("'")[1]
    file_path = safe_filename(await reply.download())
    output_ = await runcmd(f'mediainfo "{file_path}"')
    out = None
    if len(output_) != 0:
         out = output_[0]
    body_text = f"""
<h2>JSON</h2>
<pre>{x_media}</pre>
<br>
<h2>DETAILS</h2>
<pre>{out or 'Not Supported'}</pre>
"""
    text_ = media_type.split(".")[-1].upper()
    link = post_to_telegraph(media_type, body_text)
    markup = InlineKeyboardMarkup([[InlineKeyboardButton(text=text_, url=link)]])
    await process.edit_text("✨ <b>MEDIA INFO</b>", reply_markup=markup)

# =======================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 🚀

# This source code is under MIT License 📜 Unauthorized forking, importing, or using this code without giving proper credit will result in legal action ⚠️
 
# 📩 DM for permission : @TheSigmaCoder
# =======================================================


from ShiviMusic import app

from pyrogram import filters, enums
from pyrogram.types import (
    ChatMemberUpdated,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
)

from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB_URI

import asyncio
from logging import getLogger

LOGGER = getLogger(__name__)

mongo = AsyncIOMotorClient(MONGO_DB_URI)
db = mongo["Wel_DB"]
welcomedb = db["welcome_toggle_system"]


async def get_welcome(chat_id: int):
    data = await welcomedb.find_one({"chat_id": chat_id})
    if not data:
        return True
    return data.get("welcome", True)


async def enable_welcome(chat_id: int):
    await welcomedb.update_one(
        {"chat_id": chat_id},
        {"$set": {"welcome": True}},
        upsert=True
    )


async def disable_welcome(chat_id: int):
    await welcomedb.update_one(
        {"chat_id": chat_id},
        {"$set": {"welcome": False}},
        upsert=True
    )


class temp:
    MELCOW = {}


def circle(pfp, size=(720, 720), brightness_factor=1.4):
    pfp = pfp.resize(size).convert("RGBA")
    pfp = ImageEnhance.Brightness(pfp).enhance(brightness_factor)

    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)

    pfp.putalpha(mask)
    return pfp


def welcomepic(pic, user, chatname, id, uname, brightness_factor=1.3):
    background = Image.open(
        "ShiviMusic/assets/wel2.png"
    ).convert("RGBA")

    pfp = Image.open(pic).convert("RGBA")
    pfp = circle(
        pfp,
        size=(720, 720),
        brightness_factor=brightness_factor
    )

    background.paste(pfp, (520, 420), pfp)

    draw = ImageDraw.Draw(background)

    font_path = "ShiviMusic/assets/font2.ttf"

    font_id = ImageFont.truetype(font_path, 100)
    font_username = ImageFont.truetype(font_path, 100)

    username_text = f"@{uname}" if uname else "Not Set"

    draw.text(
        (1920, 1340),
        str(id),
        font=font_id,
        fill="#ffffff"
    )

    draw.text(
        (1920, 1480),
        username_text,
        font=font_username,
        fill="#ffffff"
    )

    output_path = f"downloads/welcome_{id}.png"
    background.save(output_path)

    return output_path


@app.on_message(filters.command("welcome") & filters.group)
async def welcome_cmd(_, message: Message):

    chat = message.chat
    chat_id = chat.id

    user = await app.get_chat_member(
        chat_id,
        message.from_user.id
    )

    if user.status not in (
        enums.ChatMemberStatus.ADMINISTRATOR,
        enums.ChatMemberStatus.OWNER
    ):
        return await message.reply_text(
            "**» 𝐎꯭ɴ꯭ʟ꯭ʏ ꯭༭꯭ 𝐀꯭ᴅ꯭ᴍ꯭ɪ꯭ɴ꯭s ꯭༭꯭ 𝐂꯭ᴀ꯭ɴ ꯭༭꯭ 𝐇꯭ᴀ꯭ɴ꯭ᴅ꯭ʟ꯭ᴇ ꯭༭꯭ 𝐖꯭ᴇ꯭ʟ꯭ᴄ꯭ᴏ꯭ᴍ꯭ᴇ ꯭༭꯭ 𝐒꯭ʏ꯭s꯭ᴛ꯭ᴇ꯭ᴍ**"
        )

    state = await get_welcome(chat_id)

    status = (
        "𝐄꯭ɴ꯭ᴀ꯭ʙ꯭ʟ꯭ᴇ꯭ᴅ"
        if state
        else "𝐃꯭ɪ꯭s꯭ᴀ꯭ʙ꯭ʟ꯭ᴇ꯭ᴅ"
    )

    btn = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "𝐄꯭ɴ꯭ᴀ꯭ʙ꯭ʟ꯭ᴇ",
                    callback_data=f"wlc_on_{chat_id}"
                ),
                InlineKeyboardButton(
                    "𝐃꯭ɪ꯭s꯭ᴀ꯭ʙ꯭ʟ꯭ᴇ",
                    callback_data=f"wlc_off_{chat_id}"
                )
            ]
        ]
    )

    await message.reply_text(
        f"» 𝐂꯭ᴜ꯭ʀ꯭ʀ꯭ᴇ꯭ɴ꯭ᴛ꯭ʟ꯭ʏ ꯭༭꯭ 𝐖꯭ᴇ꯭ʟ꯭ᴄ꯭ᴏ꯭ᴍ꯭ᴇ ꯭༭꯭ "
        f"𝐒꯭ᴛ꯭ᴀ꯭ᴛ꯭ᴜ꯭s **{status}** ꯭༭꯭ 𝐈꯭ɴ ꯭༭꯭ **{chat.title}**",
        reply_markup=btn
    )


@app.on_callback_query(filters.regex("wlc_"))
async def welcome_toggle(_, query):

    data = query.data.split("_")
    action = data[1]
    chat_id = int(data[2])

    member = await app.get_chat_member(
        chat_id,
        query.from_user.id
    )

    if member.status not in (
        enums.ChatMemberStatus.ADMINISTRATOR,
        enums.ChatMemberStatus.OWNER
    ):
        return await query.answer(
            "𝐘꯭ᴏ꯭ᴜ ꯭༭꯭ 𝐀꯭ʀ꯭ᴇ ꯭༭꯭ 𝐍꯭ᴏ꯭ᴛ ꯭༭꯭ 𝐀꯭ᴅ꯭ᴍ꯭ɪ꯭ɴ ꯭༭꯭ 𝐁꯭ᴀ꯭ʙ꯭ʏ 🥺",
            show_alert=True
        )

    if action == "on":
        await enable_welcome(chat_id)
        new_status = "𝐄꯭ɴ꯭ᴀ꯭ʙ꯭ʟ꯭ᴇ꯭ᴅ"
    else:
        await disable_welcome(chat_id)
        new_status = "𝐃꯭ɪ꯭s꯭ᴀ꯭ʙ꯭ʟ꯭ᴇ꯭ᴅ"

    chat = await app.get_chat(chat_id)

    await query.message.edit_text(
        f"» 𝐖꯭ᴇ꯭ʟ꯭ᴄ꯭ᴏ꯭ᴍ꯭ᴇ ꯭༭꯭ "
        f"𝐌꯭ᴇ꯭s꯭s꯭ᴀ꯭ɢ꯭ᴇ ꯭༭꯭ **{new_status}** "
        f"𝐈꯭ɴ ꯭༭꯭ **{chat.title}** "
        f"𝐁꯭ʏ ꯭༭꯭ :- **{query.from_user.mention}**"
    )

    await query.answer()


@app.on_chat_member_updated(filters.group, group=-3)
async def greet_new_member(_, member: ChatMemberUpdated):

    chat_id = member.chat.id

    is_enabled = await get_welcome(chat_id)

    if not is_enabled:
        return

    user = (
        member.new_chat_member.user
        if member.new_chat_member
        else None
    )

    if not user:
        return

    if (
        member.new_chat_member
        and not member.old_chat_member
        and member.new_chat_member.status != "kicked"
    ):

        try:
            pic = await app.download_media(
                user.photo.big_file_id,
                file_name=f"pp{user.id}.png"
            )
        except:
            pic = "ShiviMusic/assets/upic.png"

        old = temp.MELCOW.get(f"welcome-{chat_id}")

        if old:
            try:
                await old.delete()
            except:
                pass

        welcomeimg = welcomepic(
            pic,
            user.first_name,
            member.chat.title,
            user.id,
            user.username
        )

        msg = await app.send_photo(
            chat_id,
            photo=welcomeimg,
            caption=f"""
**⏤͟͟͞͞★ 𝐇꯭ᴇ꯭ʟ꯭ʟ꯭ᴏ ꯭༭꯭ 𝐃꯭ᴇ꯭ᴀ꯭ʀ ꯭༭꯭ 𝐖꯭ᴇ꯭ʟ꯭ᴄ꯭ᴏ꯭ᴍ꯭ᴇ ꯭༭꯭ 𝐓꯭ᴏ ꯭༭꯭ : {member.chat.title}**

<u>**❖ 𝐔꯭s꯭ᴇ꯭ʀ ꯭༭꯭ 𝐒꯭ʜ꯭ᴏ꯭ʀ꯭ᴛ ꯭༭꯭ 𝐈꯭ɴ꯭ꜰ꯭ᴏ**</u>

**➻ 𝐍꯭ᴀ꯭ᴍ꯭ᴇ ꯭༭꯭ »** {user.mention}
**➻ 𝐂꯭ʜ꯭ᴀ꯭ᴛ ꯭༭꯭ 𝐈꯭ᴅ ꯭༭꯭ »** `{user.id}`
**➻ 𝐔꯭_꯭𝐍꯭ᴀ꯭ᴍ꯭ᴇ ꯭༭꯭ »** @{user.username}

**➻ 𝐓꯭ʜ꯭ᴀ꯭ɴ꯭ᴋ꯭s ꯭༭꯭ 𝐅꯭ᴏ꯭ʀ ꯭༭꯭ 𝐉꯭ᴏ꯭ɪ꯭ɴ꯭ɪ꯭ɴ꯭ɢ ꯭༭꯭ 𝐔꯭s ⚡️~!
❅─────✧❅✦❅✧─────❅**
""",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "𝐀꯭ᴅ꯭ᴅ ꯭༭꯭ 𝐌꯭ᴇ ꯭༭꯭ 𝐈꯭ɴ ꯭༭꯭ 𝐘꯭ᴏ꯭ᴜ꯭ʀ ꯭༭꯭ 𝐆꯭ʀ꯭ᴏ꯭ᴜ꯭ᴘ",
                            url=f"https://t.me/{app.username}?startgroup=true"
                        )
                    ]
                ]
            )
        )

        async def delete_welcome():
            await asyncio.sleep(10)

            try:
                await msg.delete()

                if f"welcome-{chat_id}" in temp.MELCOW:
                    del temp.MELCOW[f"welcome-{chat_id}"]

            except:
                pass

        asyncio.create_task(delete_welcome())

        temp.MELCOW[f"welcome-{chat_id}"] = msg


# ======================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 😎

# 🧑‍💻 Developer : t.me/TheSigmaCoder
# 🔗 Source link : GitHub.com/Im-Notcoder/Sonali-MusicV2
# 📢 Telegram channel : t.me/Purvi_Bots
# =======================================================

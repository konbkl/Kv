# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 🚀
# Welcome System for ShiviMusic
# ===========================================================

import os
import asyncio
from logging import getLogger

from motor.motor_asyncio import AsyncIOMotorClient
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    MessageIdInvalid,
    MessageNotModified,
    UserNotParticipant,
)
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from config import MONGO_DB_URI
from ShiviMusic import app


LOGGER = getLogger(__name__)


# ===========================================================
# MongoDB
# ===========================================================

mongo = AsyncIOMotorClient(MONGO_DB_URI)

Wel_DB = mongo["ShiviMusic"]
welcome_collection = Wel_DB["welcome_toggle_system"]


# ===========================================================
# Welcome State
# ===========================================================

async def get_welcome(chat_id: int) -> bool:
    data = await welcome_collection.find_one({"chat_id": chat_id})
    return bool(data and data.get("welcome", False))


async def enable_welcome(chat_id: int):
    await welcome_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"welcome": True}},
        upsert=True,
    )


async def disable_welcome(chat_id: int):
    await welcome_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"welcome": False}},
        upsert=True,
    )


# ===========================================================
# Temporary Welcome Messages
# ===========================================================

class Temp:
    MELCOW = {}


temp = Temp()


# ===========================================================
# Directories
# ===========================================================

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# ===========================================================
# Circular Profile Photo
# ===========================================================

def circle(pfp: Image.Image, size: int = 500) -> Image.Image:
    pfp = pfp.convert("RGBA")
    pfp = pfp.resize((size, size))

    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)

    draw.ellipse(
        (0, 0, size, size),
        fill=255,
    )

    result = Image.new(
        "RGBA",
        (size, size),
        (0, 0, 0, 0),
    )

    result.paste(
        pfp,
        (0, 0),
        mask,
    )

    return result


# ===========================================================
# Welcome Image
# ===========================================================

async def welcomepic(
    user_id: int,
    first_name: str,
    username: str,
    profile_path: str,
):
    try:
        base_path = "ShiviMusic/assets/wel2.png"
        font_path = "ShiviMusic/assets/font2.ttf"

        if not os.path.exists(base_path):
            return None

        if not os.path.exists(font_path):
            return None

        background = Image.open(base_path).convert("RGBA")

        # Slight enhancement
        background = ImageEnhance.Brightness(background).enhance(1.05)

        # ---------------------------------------------------
        # Profile Photo
        # ---------------------------------------------------

        try:
            profile = Image.open(profile_path).convert("RGBA")
            profile = circle(profile, 500)

            x = (background.width - 500) // 2
            y = 50

            background.alpha_composite(
                profile,
                (x, y),
            )

        except Exception as e:
            LOGGER.warning(
                "Profile image error: %s",
                e,
            )

        # ---------------------------------------------------
        # Text
        # ---------------------------------------------------

        draw = ImageDraw.Draw(background)

        font_big = ImageFont.truetype(
            font_path,
            100,
        )

        font_small = ImageFont.truetype(
            font_path,
            65,
        )

        display_name = first_name[:18]

        # Name
        bbox = draw.textbbox(
            (0, 0),
            display_name,
            font=font_big,
        )

        text_width = bbox[2] - bbox[0]

        draw.text(
            (
                (background.width - text_width) // 2,
                580,
            ),
            display_name,
            font=font_big,
            fill="white",
        )

        # Username / ID
        info = f"@{username}" if username else f"ID: {user_id}"

        bbox = draw.textbbox(
            (0, 0),
            info,
            font=font_small,
        )

        text_width = bbox[2] - bbox[0]

        draw.text(
            (
                (background.width - text_width) // 2,
                700,
            ),
            info,
            font=font_small,
            fill="white",
        )

        # ---------------------------------------------------
        # Save
        # ---------------------------------------------------

        output_path = os.path.join(
            DOWNLOAD_DIR,
            f"welcome_{user_id}.png",
        )

        background.convert("RGB").save(
            output_path,
            quality=95,
        )

        return output_path

    except Exception as e:
        LOGGER.exception(
            "Welcome image generation failed: %s",
            e,
        )
        return None


# ===========================================================
# Admin Check
# ===========================================================

async def is_admin(chat_id: int, user_id: int) -> bool:
    try:
        member = await app.get_chat_member(
            chat_id,
            user_id,
        )

        return member.status in (
            ChatMemberStatus.OWNER,
            ChatMemberStatus.ADMINISTRATOR,
        )

    except Exception:
        return False


# ===========================================================
# /welcome Command
# ===========================================================

@app.on_message(
    filters.command("welcome")
    & filters.group
)
async def welcome_command(_, message):

    if not await is_admin(
        message.chat.id,
        message.from_user.id,
    ):
        return await message.reply_text(
            "❌ **Only group admins can use this command.**"
        )

    status = await get_welcome(
        message.chat.id,
    )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ ᴇɴᴀʙʟᴇ",
                    callback_data=f"wlc_on_{message.chat.id}",
                ),
                InlineKeyboardButton(
                    "❌ ᴅɪsᴀʙʟᴇ",
                    callback_data=f"wlc_off_{message.chat.id}",
                ),
            ]
        ]
    )

    current_status = (
        "🟢 **Enabled**"
        if status
        else "🔴 **Disabled**"
    )

    await message.reply_text(
        f"**❖ ᴡᴇʟᴄᴏᴍᴇ sʏsᴛᴇᴍ ❖**\n\n"
        f"**➻ sᴛᴀᴛᴜs »** {current_status}\n\n"
        f"ᴄʜᴏᴏsᴇ ᴀɴ ᴏᴘᴛɪᴏɴ ʙᴇʟᴏᴡ 👇",
        reply_markup=keyboard,
    )


# ===========================================================
# Welcome Callback
# ===========================================================

@app.on_callback_query(
    filters.regex(r"^wlc_(on|off)_")
)
async def welcome_callback(_, query):

    try:
        data = query.data.split("_")
        action = data[1]
        chat_id = int(data[2])

    except Exception:
        return await query.answer(
            "❌ Invalid request.",
            show_alert=True,
        )

    if not await is_admin(
        chat_id,
        query.from_user.id,
    ):
        return await query.answer(
            "❌ Only group admins can change welcome settings.",
            show_alert=True,
        )

    if action == "on":

        await enable_welcome(chat_id)

        text = (
            "🟢 **Welcome system enabled!**\n\n"
            "New members will now receive a welcome message."
        )

    else:

        await disable_welcome(chat_id)

        text = (
            "🔴 **Welcome system disabled!**\n\n"
            "New members will no longer receive welcome messages."
        )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ ᴇɴᴀʙʟᴇ",
                    callback_data=f"wlc_on_{chat_id}",
                ),
                InlineKeyboardButton(
                    "❌ ᴅɪsᴀʙʟᴇ",
                    callback_data=f"wlc_off_{chat_id}",
                ),
            ]
        ]
    )

    try:
        await query.message.edit_text(
            text,
            reply_markup=keyboard,
        )

    except MessageNotModified:
        pass

    await query.answer(
        "Updated successfully! ✅"
    )


# ===========================================================
# Text Welcome Fallback
# ===========================================================

async def send_text_welcome(
    chat_id: int,
    user,
    group_id: int,
    member_count,
    group_title: str,
):

    username = (
        f"@{user.username}"
        if user.username
        else "ɴᴏ ᴜsᴇʀɴᴀᴍᴇ"
    )

    caption = (
        f"**⏤͟͟͞͞★ ʜᴇʟʟᴏ ᴅᴇᴀʀ, ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ : "
        f"{group_title} ★**\n\n"

        f"<u>**❖ ᴜsᴇʀ ɪɴғᴏ ❖**</u>\n\n"

        f"**➻ ɴᴀᴍᴇ »** {user.mention}\n"
        f"**➻ ᴜsᴇʀ_ɪᴅ »** `{user.id}`\n"
        f"**➻ ᴜsᴇʀɴᴀᴍᴇ »** {username}\n\n"

        f"<u>**❖ ɢʀᴏᴜᴘ ɪɴғᴏ ❖**</u>\n\n"

        f"**➻ ɢʀᴏᴜᴘ_ɪᴅ »** `{group_id}`\n"
        f"**➻ ᴍᴇᴍʙᴇʀs »** `{member_count}`\n\n"

        f"**➻ ᴛʜᴀɴᴋs ғᴏʀ ᴊᴏɪɴɪɴɢ ᴜs ❤️**\n\n"

        f"**❅─────✧❅✦❅✧─────❅**"
    )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "👤 ᴠɪᴇᴡ ᴍᴇᴍʙᴇʀ",
                    user_id=user.id,
                )
            ],
            [
                InlineKeyboardButton(
                    "➕ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ",
                    url=f"https://t.me/{app.username}?startgroup=true",
                )
            ],
        ]
    )

    return await app.send_message(
        chat_id,
        caption,
        reply_markup=keyboard,
    )


# ===========================================================
# Delete Welcome After 2 Minutes
# ===========================================================

async def delete_welcome(
    chat_id: int,
    message_id: int,
    image_path: str = None,
):

    # 2 minutes
    await asyncio.sleep(120)

    try:
        await app.delete_messages(
            chat_id,
            message_id,
        )

    except (
        MessageIdInvalid,
        Exception,
    ):
        pass

    # Remove generated image
    if image_path:
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
        except Exception:
            pass

    # Remove from temp storage only
    try:
        current = temp.MELCOW.get(chat_id)

        if current == message_id:
            temp.MELCOW.pop(chat_id, None)

    except Exception:
        pass


# ===========================================================
# New Member Welcome
# ===========================================================

@app.on_chat_member_updated(
    filters.group,
    group=-3,
)
async def welcome_new_member(_, update):

    try:
        member = update.new_chat_member

        if not member:
            return

        # ---------------------------------------------------
        # Ignore bots
        # ---------------------------------------------------

        user = member.user

        if not user:
            return

        if user.is_bot:
            return

        # ---------------------------------------------------
        # Check member status
        # ---------------------------------------------------

        new_status = member.status
        old_status = update.old_chat_member.status

        valid_new_status = (
            new_status == ChatMemberStatus.MEMBER
            or new_status == ChatMemberStatus.RESTRICTED
        )

        valid_old_status = (
            old_status == ChatMemberStatus.LEFT
            or old_status == ChatMemberStatus.BANNED
        )

        if not valid_new_status:
            return

        if not valid_old_status:
            return

        chat_id = update.chat.id

        # ---------------------------------------------------
        # Check welcome enabled
        # ---------------------------------------------------

        if not await get_welcome(chat_id):
            return

        # ---------------------------------------------------
        # Group Information
        # ---------------------------------------------------

        try:
            chat = await app.get_chat(chat_id)

            group_title = (
                chat.title
                or "this group"
            )

            group_id = chat.id

            member_count = (
                chat.members_count
                if chat.members_count
                else "Unknown"
            )

        except Exception as e:

            LOGGER.warning(
                "Could not get group information: %s",
                e,
            )

            group_title = (
                update.chat.title
                or "this group"
            )

            group_id = chat_id
            member_count = "Unknown"

        # ---------------------------------------------------
        # Delete Previous Welcome
        # ---------------------------------------------------

        previous_message = temp.MELCOW.get(
            chat_id
        )

        if previous_message:

            try:
                await app.delete_messages(
                    chat_id,
                    previous_message,
                )

            except Exception:
                pass

            temp.MELCOW.pop(
                chat_id,
                None,
            )

        # ---------------------------------------------------
        # Username
        # ---------------------------------------------------

        username = (
            user.username
            if user.username
            else ""
        )

        first_name = (
            user.first_name
            or "Member"
        )

        # ---------------------------------------------------
        # Welcome Caption
        # ---------------------------------------------------

        username_text = (
            f"@{username}"
            if username
            else "ɴᴏ ᴜsᴇʀɴᴀᴍᴇ"
        )

        caption = (
            f"**⏤͟͟͞͞★ ʜᴇʟʟᴏ ᴅᴇᴀʀ, ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ : "
            f"{group_title} ★**\n\n"

            f"<u>**❖ ᴜsᴇʀ ɪɴғᴏ ❖**</u>\n\n"

            f"**➻ ɴᴀᴍᴇ »** {user.mention}\n"
            f"**➻ ᴜsᴇʀ_ɪᴅ »** `{user.id}`\n"
            f"**➻ ᴜsᴇʀɴᴀᴍᴇ »** {username_text}\n\n"

            f"<u>**❖ ɢʀᴏᴜᴘ ɪɴғᴏ ❖**</u>\n\n"

            f"**➻ ɢʀᴏᴜᴘ_ɪᴅ »** `{group_id}`\n"
            f"**➻ ᴍᴇᴍʙᴇʀs »** `{member_count}`\n\n"

            f"**➻ ᴛʜᴀɴᴋs ғᴏʀ ᴊᴏɪɴɪɴɢ ᴜs ❤️**\n\n"

            f"**❅─────✧❅✦❅✧─────❅**"
        )

        # ---------------------------------------------------
        # Buttons
        # ---------------------------------------------------

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "👤 ᴠɪᴇᴡ ᴍᴇᴍʙᴇʀ",
                        user_id=user.id,
                    )
                ],
                [
                    InlineKeyboardButton(
                        "➕ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ",
                        url=(
                            f"https://t.me/"
                            f"{app.username}"
                            f"?startgroup=true"
                        ),
                    )
                ],
            ]
        )

        # ---------------------------------------------------
        # Profile Photo
        # ---------------------------------------------------

        image_path = None

        if user.photo:

            try:
                image_path = await app.download_media(
                    user.photo.big_file_id,
                    file_name=os.path.join(
                        DOWNLOAD_DIR,
                        f"{user.id}_profile",
                    ),
                )

            except Exception as e:

                LOGGER.warning(
                    "Profile download failed: %s",
                    e,
                )

        # ---------------------------------------------------
        # Generate Welcome Image
        # ---------------------------------------------------

        welcome_image = None

        if image_path:

            welcome_image = await welcomepic(
                user.id,
                first_name,
                username,
                image_path,
            )

        # ---------------------------------------------------
        # Send Welcome
        # ---------------------------------------------------

        welcome_message = None

        try:

            if welcome_image and os.path.exists(
                welcome_image
            ):

                welcome_message = await app.send_photo(
                    chat_id,
                    photo=welcome_image,
                    caption=caption,
                    reply_markup=keyboard,
                )

            else:

                welcome_message = await app.send_message(
                    chat_id,
                    caption,
                    reply_markup=keyboard,
                )

        except Exception as e:

            LOGGER.warning(
                "Welcome message failed: %s",
                e,
            )

            # Fallback text
            try:

                welcome_message = await app.send_message(
                    chat_id,
                    caption,
                    reply_markup=keyboard,
                )

            except Exception as fallback_error:

                LOGGER.exception(
                    "Welcome fallback failed: %s",
                    fallback_error,
                )

                welcome_message = None

        # ---------------------------------------------------
        # Cleanup Profile Photo
        # ---------------------------------------------------

        if image_path:

            try:

                if os.path.exists(image_path):
                    os.remove(image_path)

            except Exception:
                pass

        # ---------------------------------------------------
        # Store & Auto Delete
        # ---------------------------------------------------

        if welcome_message:

            temp.MELCOW[
                chat_id
            ] = welcome_message.id

            asyncio.create_task(
                delete_welcome(
                    chat_id,
                    welcome_message.id,
                    welcome_image,
                )
            )

    except Exception as e:

        LOGGER.exception(
            "Welcome handler error: %s",
            e,
        )

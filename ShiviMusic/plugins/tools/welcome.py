# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 🚀
#
# ShiviMusic Welcome System
# ===========================================================

import os
import asyncio
from logging import getLogger

from motor.motor_asyncio import AsyncIOMotorClient
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import MessageIdInvalid, MessageNotModified
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
# Temporary Data
# ===========================================================

class Temp:
    MELCOW = {}


temp = Temp()


# ===========================================================
# Download Directory
# ===========================================================

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# ===========================================================
# Welcome Database Functions
# ===========================================================

async def get_welcome(chat_id: int) -> bool:
    try:
        data = await welcome_collection.find_one(
            {"chat_id": chat_id}
        )

        return bool(
            data and data.get("welcome", False)
        )

    except Exception as e:
        LOGGER.error(
            f"Welcome DB read error: {e}"
        )
        return False


async def enable_welcome(chat_id: int):
    try:
        await welcome_collection.update_one(
            {"chat_id": chat_id},
            {
                "$set": {
                    "chat_id": chat_id,
                    "welcome": True,
                }
            },
            upsert=True,
        )

    except Exception as e:
        LOGGER.error(
            f"Welcome enable error: {e}"
        )


async def disable_welcome(chat_id: int):
    try:
        await welcome_collection.update_one(
            {"chat_id": chat_id},
            {
                "$set": {
                    "chat_id": chat_id,
                    "welcome": False,
                }
            },
            upsert=True,
        )

    except Exception as e:
        LOGGER.error(
            f"Welcome disable error: {e}"
        )


# ===========================================================
# Circular Image
# ===========================================================

def circle(
    pfp: Image.Image,
    size: int = 500,
) -> Image.Image:

    pfp = pfp.convert("RGBA")
    pfp = pfp.resize(
        (size, size)
    )

    mask = Image.new(
        "L",
        (size, size),
        0,
    )

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
# Create Welcome Image
# ===========================================================

async def welcomepic(
    user_id: int,
    first_name: str,
    username: str,
    profile_path: str,
):

    try:

        background_path = (
            "ShiviMusic/assets/wel2.png"
        )

        font_path = (
            "ShiviMusic/assets/font2.ttf"
        )

        # ---------------------------------------------------
        # Check Files
        # ---------------------------------------------------

        if not os.path.exists(
            background_path
        ):
            LOGGER.warning(
                "wel2.png not found."
            )
            return None

        if not os.path.exists(
            font_path
        ):
            LOGGER.warning(
                "font2.ttf not found."
            )
            return None

        # ---------------------------------------------------
        # Open Background
        # ---------------------------------------------------

        background = Image.open(
            background_path
        ).convert("RGBA")

        background = ImageEnhance.Brightness(
            background
        ).enhance(1.05)

        # ---------------------------------------------------
        # Profile Photo
        # ---------------------------------------------------

        if (
            profile_path
            and os.path.exists(profile_path)
        ):

            try:

                profile = Image.open(
                    profile_path
                ).convert("RGBA")

                profile = circle(
                    profile,
                    500,
                )

                x = (
                    background.width - 500
                ) // 2

                y = 50

                background.alpha_composite(
                    profile,
                    (x, y),
                )

            except Exception as e:

                LOGGER.warning(
                    f"Profile image error: {e}"
                )

        # ---------------------------------------------------
        # Draw Text
        # ---------------------------------------------------

        draw = ImageDraw.Draw(
            background
        )

        font_big = ImageFont.truetype(
            font_path,
            100,
        )

        font_small = ImageFont.truetype(
            font_path,
            65,
        )

        display_name = (
            first_name[:18]
        )

        # ---------------------------------------------------
        # Name
        # ---------------------------------------------------

        bbox = draw.textbbox(
            (0, 0),
            display_name,
            font=font_big,
        )

        text_width = (
            bbox[2] - bbox[0]
        )

        draw.text(
            (
                (
                    background.width
                    - text_width
                ) // 2,
                580,
            ),
            display_name,
            font=font_big,
            fill="white",
        )

        # ---------------------------------------------------
        # Username
        # ---------------------------------------------------

        info = (
            f"@{username}"
            if username
            else f"ID: {user_id}"
        )

        bbox = draw.textbbox(
            (0, 0),
            info,
            font=font_small,
        )

        text_width = (
            bbox[2] - bbox[0]
        )

        draw.text(
            (
                (
                    background.width
                    - text_width
                ) // 2,
                700,
            ),
            info,
            font=font_small,
            fill="white",
        )

        # ---------------------------------------------------
        # Save Image
        # ---------------------------------------------------

        output_path = os.path.join(
            DOWNLOAD_DIR,
            f"welcome_{user_id}.png",
        )

        background.convert(
            "RGB"
        ).save(
            output_path,
            quality=95,
        )

        return output_path

    except Exception as e:

        LOGGER.exception(
            f"Welcome image generation error: {e}"
        )

        return None


# ===========================================================
# Admin Check
# ===========================================================

async def is_admin(
    chat_id: int,
    user_id: int,
) -> bool:

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
async def welcome_command(
    _,
    message,
):

    try:

        if not message.from_user:
            return

        # ---------------------------------------------------
        # Admin Check
        # ---------------------------------------------------

        if not await is_admin(
            message.chat.id,
            message.from_user.id,
        ):

            return await message.reply_text(
                "❌ **Only group admins can use this command.**"
            )

        # ---------------------------------------------------
        # Current Status
        # ---------------------------------------------------

        status = await get_welcome(
            message.chat.id
        )

        current_status = (
            "🟢 **Enabled**"
            if status
            else "🔴 **Disabled**"
        )

        # ---------------------------------------------------
        # Buttons
        # ---------------------------------------------------

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "✅ ᴇɴᴀʙʟᴇ",
                        callback_data=(
                            f"wlc_on_{message.chat.id}"
                        ),
                    ),
                    InlineKeyboardButton(
                        "❌ ᴅɪsᴀʙʟᴇ",
                        callback_data=(
                            f"wlc_off_{message.chat.id}"
                        ),
                    ),
                ]
            ]
        )

        await message.reply_text(
            f"**❖ ᴡᴇʟᴄᴏᴍᴇ sʏsᴛᴇᴍ ❖**\n\n"
            f"**➻ sᴛᴀᴛᴜs »** {current_status}\n\n"
            f"ᴄʜᴏᴏsᴇ ᴀɴ ᴏᴘᴛɪᴏɴ ʙᴇʟᴏᴡ 👇",
            reply_markup=keyboard,
        )

    except Exception as e:

        LOGGER.exception(
            f"/welcome command error: {e}"
        )


# ===========================================================
# Welcome Callback
# ===========================================================

@app.on_callback_query(
    filters.regex(
        r"^wlc_(on|off)_"
    )
)
async def welcome_callback(
    _,
    query,
):

    try:

        # ---------------------------------------------------
        # Parse Callback
        # ---------------------------------------------------

        parts = query.data.split("_")

        if len(parts) < 3:
            return await query.answer(
                "❌ Invalid request.",
                show_alert=True,
            )

        action = parts[1]
        chat_id = int(parts[2])

        # ---------------------------------------------------
        # Admin Check
        # ---------------------------------------------------

        if not await is_admin(
            chat_id,
            query.from_user.id,
        ):

            return await query.answer(
                "❌ Only group admins can change this setting.",
                show_alert=True,
            )

        # ---------------------------------------------------
        # Enable / Disable
        # ---------------------------------------------------

        if action == "on":

            await enable_welcome(
                chat_id
            )

            text = (
                "🟢 **Welcome system enabled!**\n\n"
                "New members will now receive welcome messages."
            )

        else:

            await disable_welcome(
                chat_id
            )

            text = (
                "🔴 **Welcome system disabled!**\n\n"
                "New members will no longer receive welcome messages."
            )

        # ---------------------------------------------------
        # Buttons
        # ---------------------------------------------------

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "✅ ᴇɴᴀʙʟᴇ",
                        callback_data=(
                            f"wlc_on_{chat_id}"
                        ),
                    ),
                    InlineKeyboardButton(
                        "❌ ᴅɪsᴀʙʟᴇ",
                        callback_data=(
                            f"wlc_off_{chat_id}"
                        ),
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

    except Exception as e:

        LOGGER.exception(
            f"Welcome callback error: {e}"
        )

        try:
            await query.answer(
                "❌ Something went wrong.",
                show_alert=True,
            )
        except Exception:
            pass


# ===========================================================
# Delete Welcome Message
# ===========================================================

async def delete_welcome(
    chat_id: int,
    message_id: int,
    image_path: str = None,
):

    try:

        # ---------------------------------------------------
        # 2 Minutes
        # ---------------------------------------------------

        await asyncio.sleep(
            120
        )

        # ---------------------------------------------------
        # Delete Message
        # ---------------------------------------------------

        try:

            await app.delete_messages(
                chat_id,
                message_id,
            )

        except MessageIdInvalid:
            pass

        except Exception as e:

            LOGGER.warning(
                f"Welcome delete error: {e}"
            )

        # ---------------------------------------------------
        # Delete Generated Image
        # ---------------------------------------------------

        if image_path:

            try:

                if os.path.exists(
                    image_path
                ):
                    os.remove(
                        image_path
                    )

            except Exception:
                pass

        # ---------------------------------------------------
        # Remove Temp Entry
        # ---------------------------------------------------

        try:

            current = temp.MELCOW.get(
                chat_id
            )

            if current == message_id:

                temp.MELCOW.pop(
                    chat_id,
                    None,
                )

        except Exception:
            pass

    except Exception as e:

        LOGGER.warning(
            f"Welcome cleanup error: {e}"
        )


# ===========================================================
# New Member Handler
# ===========================================================

@app.on_chat_member_updated(
    filters.group,
    group=-3,
)
async def welcome_new_member(
    _,
    update,
):

    try:

        # ===================================================
        # IMPORTANT FIX
        # ===================================================
        # old_chat_member can be None.
        # Never directly use:
        #
        # update.old_chat_member.status
        #
        # without checking it first.
        # ===================================================

        new_member = update.new_chat_member
        old_member = update.old_chat_member

        # ---------------------------------------------------
        # No New Member
        # ---------------------------------------------------

        if new_member is None:
            return

        # ---------------------------------------------------
        # User
        # ---------------------------------------------------

        user = new_member.user

        if user is None:
            return

        # ---------------------------------------------------
        # Ignore Bots
        # ---------------------------------------------------

        if user.is_bot:
            return

        # ---------------------------------------------------
        # New Status
        # ---------------------------------------------------

        new_status = new_member.status

        # ---------------------------------------------------
        # OLD STATUS - FIXED
        # ---------------------------------------------------

        if old_member is None:

            # Telegram may send None on a fresh join.
            old_status = ChatMemberStatus.LEFT

        else:

            old_status = old_member.status

        # ---------------------------------------------------
        # Check New Member
        # ---------------------------------------------------

        valid_new_status = (
            new_status
            in (
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.RESTRICTED,
            )
        )

        if not valid_new_status:
            return

        # ---------------------------------------------------
        # Check Previous Status
        # ---------------------------------------------------

        valid_old_status = (
            old_status
            in (
                ChatMemberStatus.LEFT,
                ChatMemberStatus.BANNED,
            )
        )

        if not valid_old_status:
            return

        # ---------------------------------------------------
        # Chat
        # ---------------------------------------------------

        chat = update.chat

        if chat is None:
            return

        chat_id = chat.id

        # ---------------------------------------------------
        # Welcome Enabled?
        # ---------------------------------------------------

        if not await get_welcome(
            chat_id
        ):
            return

        # ===================================================
        # GROUP INFORMATION
        # ===================================================

        try:

            full_chat = await app.get_chat(
                chat_id
            )

            group_title = (
                full_chat.title
                or "This Group"
            )

            group_id = full_chat.id

            member_count = (
                full_chat.members_count
                if full_chat.members_count
                is not None
                else "Unknown"
            )

        except Exception as e:

            LOGGER.warning(
                f"Group information error: {e}"
            )

            group_title = (
                chat.title
                or "This Group"
            )

            group_id = chat_id
            member_count = "Unknown"

        # ===================================================
        # DELETE PREVIOUS WELCOME
        # ===================================================

        previous_message = (
            temp.MELCOW.get(chat_id)
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

        # ===================================================
        # USER INFORMATION
        # ===================================================

        first_name = (
            user.first_name
            or "Member"
        )

        username = (
            user.username
            if user.username
            else ""
        )

        username_text = (
            f"@{username}"
            if username
            else "ɴᴏ ᴜsᴇʀɴᴀᴍᴇ"
        )

        # ===================================================
        # WELCOME CAPTION
        # ===================================================

        caption = (
            f"**⏤͟͟͞͞★ ʜᴇʟʟᴏ ᴅᴇᴀʀ, "
            f"ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ : {group_title} ★**\n\n"

            f"<u>**❖ ᴜsᴇʀ ɪɴғᴏ ❖**</u>\n\n"

            f"**➻ ɴᴀᴍᴇ »** "
            f"{user.mention}\n"

            f"**➻ ᴜsᴇʀ_ɪᴅ »** "
            f"`{user.id}`\n"

            f"**➻ ᴜsᴇʀɴᴀᴍᴇ »** "
            f"{username_text}\n\n"

            f"<u>**❖ ɢʀᴏᴜᴘ ɪɴғᴏ ❖**</u>\n\n"

            f"**➻ ɢʀᴏᴜᴘ_ɪᴅ »** "
            f"`{group_id}`\n"

            f"**➻ ᴍᴇᴍʙᴇʀs »** "
            f"`{member_count}`\n\n"

            f"**➻ ᴛʜᴀɴᴋs ғᴏʀ "
            f"ᴊᴏɪɴɪɴɢ ᴜs ❤️**\n\n"

            f"**❅─────✧❅✦❅✧─────❅**"
        )

        # ===================================================
        # BUTTONS
        # ===================================================

        bot_username = (
            getattr(
                app,
                "username",
                None,
            )
        )

        if bot_username:

            add_me_url = (
                f"https://t.me/"
                f"{bot_username}"
                f"?startgroup=true"
            )

        else:

            add_me_url = (
                "https://t.me/"
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
                        url=add_me_url,
                    )
                ],
            ]
        )

        # ===================================================
        # PROFILE IMAGE
        # ===================================================

        image_path = None
        welcome_image = None

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
                    f"Profile download error: {e}"
                )

        # ===================================================
        # CREATE WELCOME IMAGE
        # ===================================================

        if image_path:

            welcome_image = await welcomepic(
                user.id,
                first_name,
                username,
                image_path,
            )

        # ===================================================
        # SEND WELCOME
        # ===================================================

        welcome_message = None

        try:

            if (
                welcome_image
                and os.path.exists(
                    welcome_image
                )
            ):

                welcome_message = (
                    await app.send_photo(
                        chat_id,
                        photo=welcome_image,
                        caption=caption,
                        reply_markup=keyboard,
                    )
                )

            else:

                welcome_message = (
                    await app.send_message(
                        chat_id,
                        caption,
                        reply_markup=keyboard,
                    )
                )

        except Exception as e:

            LOGGER.warning(
                f"Welcome photo send failed: {e}"
            )

            # ------------------------------------------------
            # Text Fallback
            # ------------------------------------------------

            try:

                welcome_message = (
                    await app.send_message(
                        chat_id,
                        caption,
                        reply_markup=keyboard,
                    )
                )

            except Exception as fallback_error:

                LOGGER.exception(
                    f"Welcome message failed: "
                    f"{fallback_error}"
                )

        # ===================================================
        # DELETE TEMP PROFILE IMAGE
        # ===================================================

        if image_path:

            try:

                if os.path.exists(
                    image_path
                ):
                    os.remove(
                        image_path
                    )

            except Exception:
                pass

        # ===================================================
        # SAVE MESSAGE + AUTO DELETE
        # ===================================================

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

            LOGGER.info(
                f"Welcome sent to "
                f"{user.id} in {chat_id}"
            )

    except Exception as e:

        LOGGER.exception(
            f"Welcome handler error: {e}"
        )

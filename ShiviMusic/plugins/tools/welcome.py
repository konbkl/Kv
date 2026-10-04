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
# Temporary Welcome Messages
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
# Welcome Database
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
# Circular Profile Photo
# ===========================================================

def circle(
    pfp: Image.Image,
    size: int = 500,
) -> Image.Image:

    pfp = pfp.convert("RGBA")

    pfp = pfp.resize(
        (size, size),
        Image.Resampling.LANCZOS,
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
# Welcome Image
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
        # Check Background
        # ---------------------------------------------------

        if not os.path.exists(
            background_path
        ):
            LOGGER.error(
                "ShiviMusic/assets/wel2.png not found."
            )
            return None

        # ---------------------------------------------------
        # Check Font
        # ---------------------------------------------------

        if not os.path.exists(
            font_path
        ):
            LOGGER.error(
                "ShiviMusic/assets/font2.ttf not found."
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
        ).enhance(1.03)

        width = background.width
        height = background.height

        # ===================================================
        # PROFILE PHOTO
        # ===================================================

        if (
            profile_path
            and os.path.exists(profile_path)
        ):

            try:

                # Profile size
                profile_size = int(
                    min(width, height) * 0.60
                )

                profile = Image.open(
                    profile_path
                ).convert("RGBA")

                profile = circle(
                    profile,
                    profile_size,
                )

                # ------------------------------------------------
                # Position for LEFT GOLD CIRCLE
                # ------------------------------------------------

                profile_x = int(
                    width * 0.145
                )

                profile_y = int(
                    height * 0.205
                )

                background.alpha_composite(
                    profile,
                    (
                        profile_x,
                        profile_y,
                    ),
                )

            except Exception as e:

                LOGGER.warning(
                    f"Profile image error: {e}"
                )

        # ===================================================
        # DRAW TEXT
        # ===================================================

        draw = ImageDraw.Draw(
            background
        )

        # ---------------------------------------------------
        # Information Font
        # ---------------------------------------------------

        info_font_size = max(
            35,
            int(width * 0.032),
        )

        info_font = ImageFont.truetype(
            font_path,
            info_font_size,
        )

        # ===================================================
        # USER ID
        # ===================================================
        #
        # This is placed AFTER:
        #
        # User id :
        #
        # No extra ID is printed anywhere else.
        # ===================================================

        user_id_text = str(
            user_id
        )

        user_id_x = int(
            width * 0.590
        )

        user_id_y = int(
            height * 0.758
        )

        draw.text(
            (
                user_id_x,
                user_id_y,
            ),
            user_id_text,
            font=info_font,
            fill="white",
            stroke_width=1,
            stroke_fill="black",
        )

        # ===================================================
        # USERNAME
        # ===================================================

        if username:

            username_text = (
                f"@{username}"
            )

        else:

            username_text = (
                "No Username"
            )

        username_x = int(
            width * 0.590
        )

        username_y = int(
            height * 0.835
        )

        draw.text(
            (
                username_x,
                username_y,
            ),
            username_text,
            font=info_font,
            fill="white",
            stroke_width=1,
            stroke_fill="black",
        )

        # ===================================================
        # SAVE IMAGE
        # ===================================================

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
        # Status
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
        # Keyboard
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
        # IMPORTANT:
        # Group IDs are negative:
        #
        # -1001234567890
        #
        # Therefore DON'T use split("_")[2].
        # Use rsplit() instead.
        # ---------------------------------------------------

        callback_data = query.data

        if callback_data.startswith(
            "wlc_on_"
        ):

            action = "on"

            chat_id = int(
                callback_data[
                    len("wlc_on_") :
                ]
            )

        elif callback_data.startswith(
            "wlc_off_"
        ):

            action = "off"

            chat_id = int(
                callback_data[
                    len("wlc_off_") :
                ]
            )

        else:

            return await query.answer(
                "❌ Invalid request.",
                show_alert=True,
            )

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
        # Enable
        # ---------------------------------------------------

        if action == "on":

            await enable_welcome(
                chat_id
            )

            text = (
                "🟢 **Welcome system enabled!**\n\n"
                "New members will now receive welcome messages."
            )

        # ---------------------------------------------------
        # Disable
        # ---------------------------------------------------

        else:

            await disable_welcome(
                chat_id
            )

            text = (
                "🔴 **Welcome system disabled!**\n\n"
                "New members will no longer receive welcome messages."
            )

        # ---------------------------------------------------
        # Keyboard
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
# Delete Welcome After 2 Minutes
# ===========================================================

async def delete_welcome(
    chat_id: int,
    message_id: int,
    image_path: str = None,
):

    try:

        # ---------------------------------------------------
        # 2 MINUTES
        # ---------------------------------------------------

        await asyncio.sleep(
            120
        )

        # ---------------------------------------------------
        # Delete Telegram Message
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
        # Remove Temporary Message
        # ---------------------------------------------------

        try:

            current_message = (
                temp.MELCOW.get(
                    chat_id
                )
            )

            if (
                current_message
                == message_id
            ):

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
        # GET NEW / OLD MEMBER
        # ===================================================

        new_member = (
            update.new_chat_member
        )

        old_member = (
            update.old_chat_member
        )

        # ---------------------------------------------------
        # New member missing
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

        # ===================================================
        # NEW STATUS
        # ===================================================

        new_status = (
            new_member.status
        )

        # ===================================================
        # OLD STATUS
        # ===================================================
        #
        # IMPORTANT FIX:
        #
        # old_chat_member can be None.
        # ===================================================

        if old_member is None:

            old_status = (
                ChatMemberStatus.LEFT
            )

        else:

            old_status = (
                old_member.status
            )

        # ===================================================
        # CHECK NEW MEMBER
        # ===================================================

        if new_status not in (
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.RESTRICTED,
        ):

            return

        # ===================================================
        # CHECK OLD MEMBER
        # ===================================================

        if old_status not in (
            ChatMemberStatus.LEFT,
            ChatMemberStatus.BANNED,
        ):

            return

        # ===================================================
        # CHAT
        # ===================================================

        chat = update.chat

        if chat is None:
            return

        chat_id = chat.id

        # ===================================================
        # CHECK WELCOME ENABLED
        # ===================================================

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

            group_id = (
                full_chat.id
            )

            member_count = (
                full_chat.members_count
                if full_chat.members_count
                is not None
                else "Unknown"
            )

        except Exception as e:

            LOGGER.warning(
                f"Group info error: {e}"
            )

            group_title = (
                chat.title
                or "This Group"
            )

            group_id = chat_id

            member_count = (
                "Unknown"
            )

        # ===================================================
        # DELETE PREVIOUS WELCOME
        # ===================================================

        previous_message = (
            temp.MELCOW.get(
                chat_id
            )
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
        # CAPTION
        # ===================================================

        caption = (
            f"**⏤͟͟͞͞★ ʜᴇʟʟᴏ ᴅᴇᴀʀ, "
            f"ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ : "
            f"{group_title} ★**\n\n"

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
        # BOT USERNAME
        # ===================================================

        bot_username = getattr(
            app,
            "username",
            None,
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

        # ===================================================
        # BUTTONS
        # ===================================================

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
                        "➕ ᴋɪᴅɴᴀᴘ ᴍᴇ",
                        url=add_me_url,
                    )
                ],
            ]
        )

        # ===================================================
        # DOWNLOAD PROFILE PHOTO
        # ===================================================

        image_path = None
        welcome_image = None

        if user.photo:

            try:

                image_path = (
                    await app.download_media(
                        user.photo.big_file_id,
                        file_name=os.path.join(
                            DOWNLOAD_DIR,
                            f"{user.id}_profile",
                        ),
                    )
                )

            except Exception as e:

                LOGGER.warning(
                    f"Profile download error: {e}"
                )

        # ===================================================
        # CREATE WELCOME IMAGE
        # ===================================================

        if image_path:

            welcome_image = (
                await welcomepic(
                    user.id,
                    first_name,
                    username,
                    image_path,
                )
            )

        # ===================================================
        # SEND WELCOME
        # ===================================================

        welcome_message = None

        try:

            # ------------------------------------------------
            # Send Image
            # ------------------------------------------------

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

            # ------------------------------------------------
            # Send Text if image unavailable
            # ------------------------------------------------

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
                f"Welcome image send failed: {e}"
            )

            # ------------------------------------------------
            # Final Text Fallback
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
                    f"Welcome fallback failed: "
                    f"{fallback_error}"
                )

        # ===================================================
        # DELETE DOWNLOADED PROFILE
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
        # SAVE + AUTO DELETE
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
                f"Welcome sent successfully "
                f"for user {user.id} "
                f"in chat {chat_id}"
            )

    except Exception as e:

        LOGGER.exception(
            f"Welcome handler error: {e}"
        )

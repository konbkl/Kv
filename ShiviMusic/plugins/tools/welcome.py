# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 🚀
#
# ShiviMusic Welcome System
# ZERO DATABASE
# ZERO WELCOME STATE STORAGE
#
# Features:
# • No MongoDB
# • No RAM welcome settings
# • No group/user data storage
# • Welcome image
# • Circular profile
# • User ID + Username
# • Group ID + Member count
# • View Member button
# • Add bot button
# • Auto delete after 2 minutes
# • old_chat_member None error fixed
# ===========================================================

import os
import asyncio

from PIL import Image, ImageDraw, ImageFont

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import RPCError
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ShiviMusic import app, logger


# ===========================================================
# SETTINGS
# ===========================================================

DOWNLOAD_DIR = "downloads"

os.makedirs(
    DOWNLOAD_DIR,
    exist_ok=True,
)


# ===========================================================
# FONT
# ===========================================================

def get_font(size: int, bold: bool = True):

    if bold:
        font_paths = [
            "ShiviMusic/assets/font2.ttf",
            "ShiviMusic/assets/bold.ttf",
            "ShiviMusic/assets/font.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
    else:
        font_paths = [
            "ShiviMusic/assets/font.ttf",
            "ShiviMusic/assets/font2.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]

    for font_path in font_paths:

        if os.path.exists(font_path):

            try:
                return ImageFont.truetype(
                    font_path,
                    size,
                )
            except Exception:
                pass

    return ImageFont.load_default()


# ===========================================================
# CIRCLE IMAGE
# ===========================================================

def make_circle(image):

    size = min(
        image.width,
        image.height,
    )

    left = (image.width - size) // 2
    top = (image.height - size) // 2

    image = image.crop(
        (
            left,
            top,
            left + size,
            top + size,
        )
    )

    mask = Image.new(
        "L",
        (size, size),
        0,
    )

    draw = ImageDraw.Draw(mask)

    draw.ellipse(
        (
            0,
            0,
            size - 1,
            size - 1,
        ),
        fill=255,
    )

    result = Image.new(
        "RGBA",
        (size, size),
        (0, 0, 0, 0),
    )

    result.paste(
        image.convert("RGBA"),
        (0, 0),
        mask,
    )

    return result


# ===========================================================
# CREATE WELCOME IMAGE
# ===========================================================

async def create_welcome_image(
    user_id: int,
    username: str,
    profile_path=None,
):

    background_path = (
        "ShiviMusic/assets/wel2.png"
    )

    if not os.path.exists(
        background_path
    ):
        logger.warning(
            "wel2.png not found."
        )
        return None

    try:

        background = Image.open(
            background_path
        ).convert("RGBA")

    except Exception as e:

        logger.error(
            f"Welcome background error: {e}"
        )

        return None

    width, height = background.size

    # =======================================================
    # PROFILE
    # =======================================================

    profile_size = int(
        height * 0.415
    )

    profile_x = int(
        width * 0.160
    )

    profile_y = int(
        height * 0.245
    )

    if (
        profile_path
        and os.path.exists(profile_path)
    ):

        try:

            profile = Image.open(
                profile_path
            ).convert("RGBA")

            profile = make_circle(
                profile
            )

            profile = profile.resize(
                (
                    profile_size,
                    profile_size,
                ),
                Image.Resampling.LANCZOS,
            )

            background.alpha_composite(
                profile,
                (
                    profile_x,
                    profile_y,
                ),
            )

        except Exception as e:

            logger.warning(
                f"Profile image error: {e}"
            )

    # =======================================================
    # TEXT
    # =======================================================

    draw = ImageDraw.Draw(
        background
    )

    font_size = max(
        24,
        int(height * 0.060),
    )

    font = get_font(
        font_size,
        True,
    )

    username = (
        username
        or "No Username"
    )

    if len(username) > 18:

        username = (
            username[:18]
            + "..."
        )

    # =======================================================
    # USER ID
    # =======================================================

    user_id_x = int(
        width * 0.590
    )

    user_id_y = int(
        height * 0.775
    )

    draw.text(
        (
            user_id_x,
            user_id_y,
        ),
        str(user_id),
        font=font,
        fill=(
            255,
            255,
            255,
            255,
        ),
        anchor="lm",
    )

    # =======================================================
    # USERNAME
    # =======================================================

    username_x = int(
        width * 0.590
    )

    username_y = int(
        height * 0.855
    )

    draw.text(
        (
            username_x,
            username_y,
        ),
        username,
        font=font,
        fill=(
            255,
            255,
            255,
            255,
        ),
        anchor="lm",
    )

    # =======================================================
    # TEMP IMAGE
    # =======================================================

    image_path = os.path.join(
        DOWNLOAD_DIR,
        (
            f"welcome_"
            f"{user_id}_"
            f"{os.getpid()}_"
            f"{id(background)}.png"
        ),
    )

    try:

        background.convert(
            "RGB"
        ).save(
            image_path,
            "PNG",
            optimize=True,
        )

    except Exception as e:

        logger.error(
            f"Welcome image save error: {e}"
        )

        return None

    return image_path


# ===========================================================
# DELETE MESSAGE + IMAGE
# ===========================================================

async def auto_delete(
    chat_id: int,
    message_id: int,
    image_path=None,
):

    try:

        # 2 minutes
        await asyncio.sleep(
            120
        )

        # Delete Telegram message
        try:

            await app.delete_messages(
                chat_id,
                message_id,
            )

        except Exception:
            pass

        # Delete generated image
        if (
            image_path
            and os.path.exists(
                image_path
            )
        ):

            try:

                os.remove(
                    image_path
                )

            except Exception:
                pass

    except Exception as e:

        logger.warning(
            f"Welcome cleanup error: {e}"
        )


# ===========================================================
# NEW MEMBER HANDLER
# ===========================================================

@app.on_chat_member_updated(
    filters.group,
    group=-3,
)
async def welcome_new_member(
    client,
    update,
):

    try:

        # ===================================================
        # IMPORTANT FIX
        #
        # old_chat_member can be None.
        # ===================================================

        new_member = (
            update.new_chat_member
        )

        old_member = (
            update.old_chat_member
        )

        if new_member is None:
            return

        user = new_member.user

        if user is None:
            return

        # Don't welcome bots
        if user.is_bot:
            return

        # ===================================================
        # STATUS CHECK
        # ===================================================

        new_status = (
            new_member.status
        )

        if old_member is None:

            old_status = (
                ChatMemberStatus.LEFT
            )

        else:

            old_status = (
                old_member.status
            )

        # User must become member/restricted
        if new_status not in (
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.RESTRICTED,
        ):
            return

        # User must come from left/banned state
        if old_status not in (
            ChatMemberStatus.LEFT,
            ChatMemberStatus.BANNED,
        ):
            return

        chat = update.chat

        if chat is None:
            return

        chat_id = chat.id

        # ===================================================
        # CHAT INFORMATION
        # ===================================================

        try:

            full_chat = await app.get_chat(
                chat_id
            )

            group_name = (
                full_chat.title
                or chat.title
                or "Group"
            )

            members_count = (
                full_chat.members_count
                or 0
            )

        except Exception:

            group_name = (
                chat.title
                or "Group"
            )

            members_count = 0

        # ===================================================
        # USERNAME
        # ===================================================

        if user.username:

            username = (
                "@"
                + user.username
            )

        else:

            username = (
                user.first_name
                or "User"
            )

        # ===================================================
        # DOWNLOAD PROFILE
        # ===================================================

        profile_path = None

        if user.photo:

            try:

                profile_path = os.path.join(
                    DOWNLOAD_DIR,
                    (
                        f"profile_"
                        f"{user.id}_"
                        f"{os.getpid()}_"
                        f"{id(update)}.jpg"
                    ),
                )

                await app.download_media(
                    user.photo.big_file_id,
                    file_name=profile_path,
                )

            except Exception as e:

                profile_path = None

                logger.warning(
                    f"Profile download failed: {e}"
                )

        # ===================================================
        # CREATE WELCOME IMAGE
        # ===================================================

        image_path = (
            await create_welcome_image(
                user_id=user.id,
                username=username,
                profile_path=profile_path,
            )
        )

        # Remove downloaded profile immediately
        if (
            profile_path
            and os.path.exists(
                profile_path
            )
        ):

            try:

                os.remove(
                    profile_path
                )

            except Exception:
                pass

        # ===================================================
        # WELCOME TEXT
        # ===================================================

        welcome_text = (
            f"👋 ʜᴇʏ {username}!\n\n"
            f"✨ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ "
            f"{group_name}\n"
            f"👥 ᴍᴇᴍʙᴇʀs: "
            f"{members_count}\n"
            f"🆔 ɢʀᴏᴜᴘ ɪᴅ: "
            f"`{chat_id}`"
        )

        # ===================================================
        # BOT USERNAME
        # ===================================================

        try:

            bot_username = (
                await app.get_me()
            ).username

        except Exception:

            bot_username = None

        # ===================================================
        # BUTTONS
        #
        # Telegram doesn't provide an API to set the
        # actual background color of InlineKeyboardButton.
        # Green/blue emoji are used instead.
        # ===================================================

        buttons = [
            [
                InlineKeyboardButton(
                    "🟢 ᴠɪᴇᴡ ᴍᴇᴍʙᴇʀ",
                    user_id=user.id,
                )
            ]
        ]

        if bot_username:

            buttons.append(
                [
                    InlineKeyboardButton(
                        "🔵 ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ",
                        url=(
                            "https://t.me/"
                            f"{bot_username}"
                            "?startgroup=true"
                        ),
                    )
                ]
            )

        reply_markup = (
            InlineKeyboardMarkup(
                buttons
            )
        )

        # ===================================================
        # SEND WELCOME
        # ===================================================

        sent_message = None

        if (
            image_path
            and os.path.exists(
                image_path
            )
        ):

            try:

                sent_message = (
                    await app.send_photo(
                        chat_id=chat_id,
                        photo=image_path,
                        caption=welcome_text,
                        reply_markup=reply_markup,
                    )
                )

            except Exception as e:

                logger.warning(
                    f"Welcome photo send failed: {e}"
                )

        # ===================================================
        # FALLBACK TEXT
        # ===================================================

        if sent_message is None:

            try:

                sent_message = (
                    await app.send_message(
                        chat_id=chat_id,
                        text=welcome_text,
                        reply_markup=reply_markup,
                    )
                )

            except Exception as e:

                logger.error(
                    f"Welcome send error: {e}"
                )

                if (
                    image_path
                    and os.path.exists(
                        image_path
                    )
                ):

                    try:
                        os.remove(
                            image_path
                        )
                    except Exception:
                        pass

                return

        # ===================================================
        # AUTO DELETE
        #
        # Nothing is stored in MongoDB or RAM.
        # The task only exists until it finishes.
        # ===================================================

        asyncio.create_task(
            auto_delete(
                chat_id=chat_id,
                message_id=sent_message.id,
                image_path=image_path,
            )
        )

    except Exception as e:

        logger.exception(
            f"Welcome handler error: {e}"
        )

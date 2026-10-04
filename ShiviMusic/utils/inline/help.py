# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 🚀
#
# This source code is under MIT License 📜
# ❌ Unauthorized forking, importing, or using this code
#    without giving proper credit will result in legal action ⚠️
#
# 📩 DM for permission : @TheSigmaCoder
# ===========================================================

from typing import Union

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ShiviMusic import app


def help_pannel(_, START: Union[bool, int] = None):
    first = [
        InlineKeyboardButton(
            text="꯭˹ ꯭𝐂꯭ʟ꯭ᴏ꯭s꯭ᴇ ꯭˼",
            callback_data="close",
        )
    ]

    second = [
        InlineKeyboardButton(
            text="꯭⌯ ꯭𝐁꯭ᴀ꯭ᴄ꯭ᴋ ꯭⌯",
            callback_data="settingsback_helper",
        ),
    ]

    mark = second if START else first

    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["H_B_25"],
                    callback_data="help_callback hb1",
                ),
                InlineKeyboardButton(
                    text=_["H_B_26"],
                    callback_data="help_callback hb2",
                ),
                InlineKeyboardButton(
                    text=_["H_B_28"],
                    callback_data="help_callback hb3",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=_["H_B_27"],
                    callback_data="help_callback hb4",
                ),
                InlineKeyboardButton(
                    text=_["H_B_31"],
                    callback_data="help_callback hb5",
                ),
                InlineKeyboardButton(
                    text=_["H_B_29"],
                    callback_data="help_callback hb6",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=_["H_B_33"],
                    callback_data="help_callback hb7",
                ),
                InlineKeyboardButton(
                    text=_["H_B_30"],
                    callback_data="help_callback hb8",
                ),
                InlineKeyboardButton(
                    text=_["H_B_32"],
                    callback_data="help_callback hb9",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="꯭• ꯭𝐖꯭ᴇ꯭ʟ꯭ᴄ꯭ᴏ꯭ᴍ꯭ᴇ ꯭•",
                    callback_data="help_callback hb10",
                ),
                InlineKeyboardButton(
                    text="꯭• ꯭𝐋꯭ᴏ꯭ᴄ꯭ᴋ꯭s ꯭•",
                    callback_data="help_callback hb11",
                ),
                InlineKeyboardButton(
                    text="꯭• ꯭𝐍꯭ɪ꯭ɢ꯭ʜ꯭ᴛ꯭ᴍ꯭ᴏ꯭ᴅ꯭ᴇ ꯭•",
                    callback_data="help_callback hb12",
                ),
            ],
            mark,
        ]
    )

    return upl


def help_back_markup(_):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="꯭⌯ ꯭𝐁꯭ᴀ꯭ᴄ꯭ᴋ ꯭⌯",
                    callback_data="settings_back_helper",
                ),
            ]
        ]
    )

    return upl


def private_help_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="꯭˹ ꯭𝐇꯭ᴇ꯭ʟ꯭ᴘ ꯭& ꯭𝐂꯭ᴏ꯭ᴍ꯭ᴍ꯭ᴀ꯭ɴ꯭ᴅ꯭s ꯭˼",
                url=f"https://t.me/{app.username}?start=help",
            ),
        ],
    ]

    return buttons


# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (Im-Notcoder) 😎
#
# 🧑‍💻 Developer : t.me/TheSigmaCoder
# 🔗 Source link : GitHub.com/Im-Notcoder/Shivi-V2
# 📢 Telegram channel : t.me/Purvi_Bots
# ===========================================================

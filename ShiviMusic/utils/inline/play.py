import math
import random
from pyrogram import enums
from pyrogram.enums import ButtonStyle
from pyrogram.types import InlineKeyboardButton
from AarumiMusic.utils.formatters import time_to_seconds
from AarumiMusic import app

STYLES = [
    enums.ButtonStyle.PRIMARY,
    enums.ButtonStyle.SUCCESS,
    enums.ButtonStyle.DANGER
]

def track_markup(_, videoid, user_id, channel, fplay):
    alone_style = random.choice(STYLES)
    group_style = random.choice([s for s in STYLES if s != alone_style])
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}", style=group_style
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}", style=group_style
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}", style=alone_style
            )
        ],
    ]
    return buttons


def stream_markup_timer(_, chat_id, played, dur):
    style_progress = random.choice(STYLES)
    style_controls = random.choice(STYLES)
    style_seek = random.choice(STYLES)
    style_close = random.choice(STYLES)
    style_add = random.choice([s for s in STYLES if s != style_close])
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)

    remaining_sec = duration_sec - played_sec
    if remaining_sec < 0:
        remaining_sec = 0

    rem_min = remaining_sec // 60
    rem_sec = remaining_sec % 60
    remaining = f"{rem_min:02d}:{rem_sec:02d}"

    percentage = (played_sec / duration_sec) * 100 if duration_sec else 0
    umm = math.floor(percentage)

    if 0 < umm <= 10:
        bar = "|♬—————————| -"
    elif 10 < umm < 20:
        bar = "|—♬————————| -"
    elif 20 <= umm < 30:
        bar = "|——♬———————| -"
    elif 30 <= umm < 40:
        bar = "|———♬——————| -"
    elif 40 <= umm < 50:
        bar = "|————♬—————| -"
    elif 50 <= umm < 60:
        bar = "|—————♬————| -"
    elif 60 <= umm < 70:
        bar = "|——————♬———| -"
    elif 70 <= umm < 80:
        bar = "|———————♬——| -"
    elif 80 <= umm < 95:
        bar = "|————————♬—| -"
    else:
        bar = "|—————————♬| -"

    buttons = [
        [
            InlineKeyboardButton(
                text=f"{played} {bar} {remaining}",
                callback_data="api_status",
                style=style_progress,
            ),
            InlineKeyboardButton(
                text="➕",
                url=f"https://t.me/{app.username}?startgroup=true",
                style=style_add,
            ),
        ],
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}", style=style_controls),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}", style=style_controls),
            InlineKeyboardButton(text="↻", callback_data=f"ADMIN Replay|{chat_id}", style=style_controls),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style=style_controls),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}", style=style_controls),
        ],
        [
            InlineKeyboardButton(text="-20ˢ", callback_data=f"ADMIN SeekBack|{chat_id}", style=style_seek),
            InlineKeyboardButton(text="ɪɴғᴏ", callback_data="api_status", style=style_seek),
            InlineKeyboardButton(text="20ˢ+", callback_data=f"ADMIN SeekFwd|{chat_id}", style=style_seek),
        ],
        [
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close", style=style_close),
            InlineKeyboardButton(
                text="➕ ᴀᴅᴅ ᴍᴇ",
                url=f"https://t.me/{app.username}?startgroup=true",
                style=style_add,
            ),
        ],
    ]
    return buttons


def stream_markup(_, chat_id):
    style_controls = random.choice(STYLES)
    style_seek = random.choice(STYLES)
    style_close = random.choice(STYLES)
    style_add = random.choice([s for s in STYLES if s != style_close])

    buttons = [
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}", style=style_controls),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}", style=style_controls),
            InlineKeyboardButton(text="↻", callback_data=f"ADMIN Replay|{chat_id}", style=style_controls),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style=style_controls),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}", style=style_controls),
        ],
        [
            InlineKeyboardButton(text="-20ˢ", callback_data=f"ADMIN SeekBack|{chat_id}", style=style_seek),
            InlineKeyboardButton(text="ɪɴғᴏ", callback_data="api_status", style=style_seek),
            InlineKeyboardButton(text="20ˢ+", callback_data=f"ADMIN SeekFwd|{chat_id}", style=style_seek),
        ],
        [
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close", style=style_close),
            InlineKeyboardButton(
                text="➕ ᴀᴅᴅ ᴍᴇ",
                url=f"https://t.me/{app.username}?startgroup=true",
                style=style_add,
            ),
        ],
    ]
    return buttons


def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    alone_style = random.choice(STYLES)
    group_style = random.choice([s for s in STYLES if s != alone_style])

    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"LuckyPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}",
                style=group_style
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"LuckyPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}",
                style=group_style
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
                style=alone_style
            ),
        ],
    ]
    return buttons


def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    alone_style = random.choice(STYLES)

    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_3"],
                callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}",
                style=alone_style
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
                style=alone_style
            ),
        ],
    ]
    return buttons


def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    alone_style = random.choice(STYLES)
    group_style = random.choice([s for s in STYLES if s != alone_style])

    query = f"{query[:20]}"
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
                style=group_style
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
                style=group_style
            ),
        ],
        [
            InlineKeyboardButton(
                text="◁",
                callback_data=f"slider B|{query_type}|{query}|{user_id}|{channel}|{fplay}",
                style=group_style
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {query}|{user_id}",
                style=group_style
            ),
            InlineKeyboardButton(
                text="▷",
                callback_data=f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}",
                style=group_style
            ),
        ],
    ]
    return buttons

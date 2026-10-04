# ===========================================================
# ShiviMusic - Premium Custom Emoji Helper
# Telegram HTML Custom Emoji Support
# ===========================================================

from typing import Optional


PREMIUM_EMOJIS = {
    "✨": "5368324170671202286",
    "⭐": "5368324170671202285",
    "🔥": "5372454798370865251",
    "❤️": "5372454798947254454",
    "💚": "5372454798433394840",
    "💛": "5372454799385092096",
    "💎": "5372454798736294012",
    "👑": "5372454798855848155",
    "🏆": "5372454799210578124",
    "🚀": "5372454798899183807",
    "📢": "5372454799291646038",
    "🎯": "5372454798468563054",
    "🤖": "5372454798760976435",
    "✅": "5372454798532517339",
    "❌": "5372454798760976436",
    "🟢": "5372454798561905212",
    "🔴": "5372454799092687027",
    "🟡": "5372454799447621689",
    "🔵": "5372454798532517340",
    "⚡": "5843553939672274145",
    "ℹ️": "5258503720928288433",
    "⚙️": "5258420634785947640",
    "⬅️": "5877536313623711363",
    "🏠": "5807868868886009920",
    "📄": "5258477770735885832",
    "📁": "5875206779196935950",
    "⬇️": "5258336354642697821",
    "⬆️": "5260652420052032852",
    "⚠️": "5258474669769497337",
    "💫": "5368324170671202286",
}


def premium_emoji(emoji: str) -> str:
    """
    Convert normal emoji to Telegram custom emoji HTML.
    """

    emoji_id: Optional[str] = PREMIUM_EMOJIS.get(emoji)

    if not emoji_id:
        return emoji

    return f'<tg-emoji emoji-id="{emoji_id}">{emoji}</tg-emoji>'


def premiumize(text: str) -> str:
    """
    Convert all supported emojis inside text
    to Telegram custom emojis.
    """

    if not text:
        return text

    # Longest first.
    for emoji in sorted(PREMIUM_EMOJIS, key=len, reverse=True):
        replacement = premium_emoji(emoji)
        text = text.replace(emoji, replacement)

    return text

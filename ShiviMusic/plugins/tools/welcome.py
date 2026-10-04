# ===========================================================
# New Member Welcome - FIXED
# ===========================================================

@app.on_chat_member_updated(
    filters.group,
    group=-3,
)
async def welcome_new_member(_, update):

    try:
        # ---------------------------------------------------
        # Safely get chat members
        # ---------------------------------------------------

        new_member = update.new_chat_member
        old_member = update.old_chat_member

        # Telegram/Pyrogram can send updates where one of
        # these values is None.
        if new_member is None:
            return

        user = new_member.user

        if user is None:
            return

        # Ignore bots
        if user.is_bot:
            return

        # ---------------------------------------------------
        # New status
        # ---------------------------------------------------

        new_status = new_member.status

        # ---------------------------------------------------
        # OLD STATUS FIX
        # ---------------------------------------------------
        # old_chat_member can be None for some join events.
        # Treat None as LEFT so a genuine new join is accepted.

        if old_member is None:
            old_status = ChatMemberStatus.LEFT
        else:
            old_status = old_member.status

        # ---------------------------------------------------
        # Check join condition
        # ---------------------------------------------------

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

        # ---------------------------------------------------
        # Chat ID
        # ---------------------------------------------------

        chat_id = update.chat.id

        # ---------------------------------------------------
        # Check Welcome System
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
                or "This Group"
            )

            group_id = chat.id

            member_count = (
                chat.members_count
                if chat.members_count is not None
                else "Unknown"
            )

        except Exception as e:

            LOGGER.warning(
                f"Failed to get group information: {e}"
            )

            group_title = (
                update.chat.title
                or "This Group"
            )

            group_id = chat_id
            member_count = "Unknown"

        # ---------------------------------------------------
        # Delete Previous Welcome
        # ---------------------------------------------------

        previous_message = temp.MELCOW.get(chat_id)

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
        # User Information
        # ---------------------------------------------------

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

        # ---------------------------------------------------
        # Welcome Caption
        # ---------------------------------------------------

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
        # Download Profile
        # ---------------------------------------------------

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
                    f"Profile download failed: {e}"
                )

        # ---------------------------------------------------
        # Generate Welcome Image
        # ---------------------------------------------------

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

            if (
                welcome_image
                and os.path.exists(welcome_image)
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
                f"Welcome photo failed: {e}"
            )

            # Text fallback
            try:

                welcome_message = await app.send_message(
                    chat_id,
                    caption,
                    reply_markup=keyboard,
                )

            except Exception as fallback_error:

                LOGGER.error(
                    f"Welcome message failed: "
                    f"{fallback_error}"
                )

        # ---------------------------------------------------
        # Remove Downloaded Profile
        # ---------------------------------------------------

        if image_path:

            try:

                if os.path.exists(image_path):
                    os.remove(image_path)

            except Exception:
                pass

        # ---------------------------------------------------
        # Store Message + Auto Delete
        # ---------------------------------------------------

        if welcome_message:

            temp.MELCOW[chat_id] = (
                welcome_message.id
            )

            # Delete after 2 minutes
            asyncio.create_task(
                delete_welcome(
                    chat_id,
                    welcome_message.id,
                    welcome_image,
                )
            )

    except Exception as e:

        LOGGER.exception(
            f"Welcome handler error: {e}"
        )

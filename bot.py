"""
Group Management Bot - @clerkmm Development
All admin commands work for ALL group admins
Promote/Demote included | /panel for all admins
"""

import logging
from datetime import datetime, timedelta
from typing import Dict

from telegram import Update, ChatPermissions, ChatAdministratorRights, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext

# ============ CONFIGURATION ============
BOT_TOKEN = "8796595625:AAF2GXdlB244GK5TDXMBdFdMtzXgmna6cKw"
OWNER_ID = 8558052873  # Bot owner (you)
# =======================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data storage
warnings: Dict[int, Dict[int, int]] = {}
filters_dict: Dict[int, Dict[str, str]] = {}
welcome_msgs: Dict[int, str] = {}

async def is_admin(update: Update, user_id: int) -> bool:
    """Check if user is admin in the group"""
    try:
        member = await update.effective_chat.get_member(user_id)
        return member.status in ['administrator', 'creator']
    except:
        return False

async def is_bot_admin(update: Update, context: CallbackContext) -> bool:
    """Check if bot is admin in the group"""
    try:
        bot_member = await update.effective_chat.get_member(context.bot.id)
        return bot_member.status in ['administrator', 'creator']
    except:
        return False

# ============ ADMIN PANEL (For ALL Admins) ============
async def panel(update: Update, context: CallbackContext):
    """Open admin panel - /panel (works for ALL admins)"""
    if not await is_admin(update, update.effective_user.id):
        await update.message.reply_text("❌ Admin only command!")
        return
    
    keyboard = [
        [InlineKeyboardButton("👑 Moderation", callback_data="menu_mod")],
        [InlineKeyboardButton("🔒 Locks", callback_data="menu_lock")],
        [InlineKeyboardButton("🎯 Filters", callback_data="menu_filter")],
        [InlineKeyboardButton("💬 Welcome", callback_data="menu_welcome")],
        [InlineKeyboardButton("📊 Stats", callback_data="menu_stats")],
        [InlineKeyboardButton("⭐ Promote/Demote", callback_data="menu_promote")],
        [InlineKeyboardButton("❌ Close", callback_data="menu_close")]
    ]
    await update.message.reply_text("🔧 **Admin Panel**\nSelect an option:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def menu_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat = update.effective_chat
    
    if data == "menu_mod":
        keyboard = [
            [InlineKeyboardButton("🔨 Ban", callback_data="action_ban"), InlineKeyboardButton("🔇 Mute", callback_data="action_mute")],
            [InlineKeyboardButton("⚠️ Warn", callback_data="action_warn"), InlineKeyboardButton("🔊 Unmute", callback_data="action_unmute")],
            [InlineKeyboardButton("🧹 Purge", callback_data="action_purge"), InlineKeyboardButton("✅ Unwarn", callback_data="action_unwarn")],
            [InlineKeyboardButton("◀️ Back", callback_data="menu_back")]
        ]
        await query.edit_message_text("👑 **Moderation Tools**\nReply to a user and click a button:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "menu_promote":
        keyboard = [
            [InlineKeyboardButton("⭐ Promote to Admin", callback_data="action_promote")],
            [InlineKeyboardButton("📉 Demote to Member", callback_data="action_demote")],
            [InlineKeyboardButton("◀️ Back", callback_data="menu_back")]
        ]
        await query.edit_message_text("⭐ **Promote/Demote**\nReply to a user and click a button:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "menu_lock":
        keyboard = [
            [InlineKeyboardButton("🔒 Lock All", callback_data="lock_all"), InlineKeyboardButton("🔓 Unlock All", callback_data="unlock_all")],
            [InlineKeyboardButton("🔗 Links", callback_data="lock_links"), InlineKeyboardButton("🖼️ Media", callback_data="lock_media")],
            [InlineKeyboardButton("📨 Forwards", callback_data="lock_forward"), InlineKeyboardButton("🎤 Voice", callback_data="lock_voice")],
            [InlineKeyboardButton("◀️ Back", callback_data="menu_back")]
        ]
        await query.edit_message_text("🔒 **Lock Settings**", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "menu_filter":
        keyboard = [
            [InlineKeyboardButton("➕ Add Filter", callback_data="filter_add")],
            [InlineKeyboardButton("📋 List Filters", callback_data="filter_list")],
            [InlineKeyboardButton("❌ Delete Filter", callback_data="filter_del")],
            [InlineKeyboardButton("◀️ Back", callback_data="menu_back")]
        ]
        await query.edit_message_text("🎯 **Filter Management**\nUse /filter <word> <reply> to add", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "menu_welcome":
        keyboard = [
            [InlineKeyboardButton("📝 Set Welcome", callback_data="welcome_set")],
            [InlineKeyboardButton("❌ Remove Welcome", callback_data="welcome_remove")],
            [InlineKeyboardButton("◀️ Back", callback_data="menu_back")]
        ]
        await query.edit_message_text("💬 **Welcome Message**\nUse /setwelcome <message>\nUse {user} for user name", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "menu_stats":
        try:
            members = await chat.get_member_count()
            filters_count = len(filters_dict.get(chat.id, {}))
            await query.edit_message_text(f"📊 **Group Stats**\n\nMembers: {members}\nFilters: {filters_count}", parse_mode="Markdown")
        except:
            await query.edit_message_text("Unable to fetch stats.")
    
    elif data == "menu_back":
        keyboard = [
            [InlineKeyboardButton("👑 Moderation", callback_data="menu_mod")],
            [InlineKeyboardButton("🔒 Locks", callback_data="menu_lock")],
            [InlineKeyboardButton("🎯 Filters", callback_data="menu_filter")],
            [InlineKeyboardButton("💬 Welcome", callback_data="menu_welcome")],
            [InlineKeyboardButton("📊 Stats", callback_data="menu_stats")],
            [InlineKeyboardButton("⭐ Promote/Demote", callback_data="menu_promote")],
            [InlineKeyboardButton("❌ Close", callback_data="menu_close")]
        ]
        await query.edit_message_text("🔧 **Admin Panel**\nSelect an option:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "menu_close":
        await query.edit_message_text("✅ Panel closed.")
    
    # Lock actions
    elif data == "lock_all":
        context.chat_data['locked'] = True
        await context.bot.set_chat_permissions(chat.id, ChatPermissions(can_send_messages=False))
        await query.edit_message_text("🔒 Everything locked!")
    elif data == "unlock_all":
        context.chat_data['locked'] = False
        perms = ChatPermissions(can_send_messages=True, can_send_photos=True, can_send_videos=True, can_send_audios=True, can_send_documents=True, can_send_voice_notes=True, can_send_polls=True, can_send_other_messages=True)
        await context.bot.set_chat_permissions(chat.id, perms)
        await query.edit_message_text("🔓 Everything unlocked!")
    elif data == "lock_links":
        context.chat_data['lock_links'] = True
        await query.edit_message_text("🔒 Links locked!")
    elif data == "lock_media":
        context.chat_data['lock_media'] = True
        await query.edit_message_text("🔒 Media locked!")
    elif data == "lock_forward":
        context.chat_data['lock_forward'] = True
        await query.edit_message_text("🔒 Forwards locked!")
    elif data == "lock_voice":
        context.chat_data['lock_voice'] = True
        await query.edit_message_text("🔒 Voice messages locked!")

# ============ PROMOTE/DEMOTE COMMANDS ============
async def promote(update: Update, context: CallbackContext):
    """Promote a user to admin - /promote"""
    if not await is_admin(update, update.effective_user.id):
        await update.message.reply_text("❌ Admin only!")
        return
    
    if not await is_bot_admin(update, context):
        await update.message.reply_text("❌ I need to be admin first!")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply to a user to promote.")
        return
    
    user_id = update.message.reply_to_message.from_user.id
    user = update.message.reply_to_message.from_user
    
    # Can't promote bot owner or yourself
    if user_id == OWNER_ID:
        await update.message.reply_text("❌ Cannot promote bot owner!")
        return
    if user_id == context.bot.id:
        await update.message.reply_text("❌ Cannot promote myself!")
        return
    
    try:
        # Promote with all rights
        await context.bot.promote_chat_member(
            update.effective_chat.id, user_id,
            can_change_info=True,
            can_post_messages=True,
            can_edit_messages=True,
            can_delete_messages=True,
            can_invite_users=True,
            can_restrict_members=True,
            can_pin_messages=True,
            can_promote_members=False
        )
        await update.message.reply_text(f"✅ {user.first_name} is now an admin!")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed: {str(e)}")

async def demote(update: Update, context: CallbackContext):
    """Demote an admin to member - /demote"""
    if not await is_admin(update, update.effective_user.id):
        await update.message.reply_text("❌ Admin only!")
        return
    
    if not await is_bot_admin(update, context):
        await update.message.reply_text("❌ I need to be admin first!")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply to a user to demote.")
        return
    
    user_id = update.message.reply_to_message.from_user.id
    user = update.message.reply_to_message.from_user
    
    if user_id == OWNER_ID:
        await update.message.reply_text("❌ Cannot demote bot owner!")
        return
    
    try:
        # Remove all admin rights
        await context.bot.promote_chat_member(
            update.effective_chat.id, user_id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False
        )
        await update.message.reply_text(f"✅ {user.first_name} is no longer an admin!")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed: {str(e)}")

# ============ MODERATION COMMANDS ============
async def ban(update: Update, context: CallbackContext):
    if not await is_admin(update, update.effective_user.id):
        await update.message.reply_text("❌ Admin only!")
        return
    if not await is_bot_admin(update, context):
        await update.message.reply_text("❌ I need to be admin first!")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply to a user to ban.")
        return
    user_id = update.message.reply_to_message.from_user.id
    await context.bot.ban_chat_member(update.effective_chat.id, user_id)
    await update.message.reply_text("✅ Banned!")

async def mute(update: Update, context: CallbackContext):
    if not await is_admin(update, update.effective_user.id):
        await update.message.reply_text("❌ Admin only!")
        return
    if not await is_bot_admin(update, context):
        await update.message.reply_text("❌ I need to be admin first!")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply to a user to mute.")
        return
    minutes = int(context.args[0]) if context.args and context.args[0].isdigit() else 5
    user_id = update.message.reply_to_message.from_user.id
    until = datetime.now() + timedelta(minutes=minutes)
    await context.bot.restrict_chat_member(update.effective_chat.id, user_id, ChatPermissions(can_send_messages=False), until_date=until)
    await update.message.reply_text(f"🔇 Muted for {minutes} minutes")

async def unmute(update: Update, context: CallbackContext):
    if not await is_admin(update, update.effective_user.id):
        await update.message.reply_text("❌ Admin only!")
        return
    if not await is_bot_admin(update, context):
        await update.message.reply_text("❌ I need to be admin first!")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply to a user to unmute.")
        return
    user_id = update.message.reply_to_message.from_user.id
    perms = ChatPermissions(can_send_messages=True, can_send_photos=True, can_send_videos=True, can_send_audios=True, can_send_documents=True, can_send_voice_notes=True, can_send_polls=True, can_send_other_messages=True)
    await context.bot.restrict_chat_member(update.effective_chat.id, user_id, perms)
    await update.message.reply_text("✅ Unmuted")

async def warn(update: Update, context: CallbackContext):
    if not await is_admin(update, update.effective_user.id):
        await update.message.reply_text("❌ Admin only!")
        return
    if not await is_bot_admin(update, context):
        await update.message.reply_text("❌ I need to be admin first!")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply to a user to warn.")
        return
    chat_id = update.effective_chat.id
    user_id = update.message.reply_to_message.from_user.id
    if chat_id not in warnings:
        warnings[chat_id] = {}
    warnings[chat_id][user_id] = warnings[chat_id].get(user_id, 0) + 1
    count = warnings[chat_id][user_id]
    await update.message.reply_text(f"⚠️ Warned! ({count}/3)")
    if count >= 3:
        await context.bot.ban_chat_member(chat_id, user_id)
        await update.message.reply_text("🚫 Banned for 3 warnings!")

async def unwarn(update: Update, context: CallbackContext):
    if not await is_admin(update, update.effective_user.id):
        await update.message.reply_text("❌ Admin only!")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply to a user to unwarn.")
        return
    chat_id = update.effective_chat.id
    user_id = update.message.reply_to_message.from_user.id
    if chat_id in warnings and user_id in warnings[chat_id]:
        del warnings[chat_id][user_id]
        await update.message.reply_text("✅ Warning removed")

async def purge(update: Update, context: CallbackContext):
    if not await is_admin(update, update.effective_user.id):
        await update.message.reply_text("❌ Admin only!")
        return
    if not await is_bot_admin(update, context):
        await update.message.reply_text("❌ I need to be admin first!")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply to a message to purge from there.")
        return
    start = update.message.reply_to_message.message_id
    end = update.message.message_id
    deleted = 0
    for msg_id in range(start, end):
        try:
            await context.bot.delete_message(update.effective_chat.id, msg_id)
            deleted += 1
        except:
            pass
    await update.message.reply_text(f"🧹 Deleted {deleted} messages")

async def info(update: Update, context: CallbackContext):
    """Get user info - /info"""
    user = update.message.reply_to_message.from_user if update.message.reply_to_message else update.effective_user
    text = f"**User Info**\n\nName: {user.first_name}\nID: `{user.id}`"
    if user.username:
        text += f"\nUsername: @{user.username}"
    await update.message.reply_text(text, parse_mode="Markdown")

# ============ FILTERS ============
async def set_filter(update: Update, context: CallbackContext):
    if not await is_admin(update, update.effective_user.id):
        await update.message.reply_text("❌ Admin only!")
        return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /filter <word> <reply>")
        return
    word = context.args[0].lower()
    reply = " ".join(context.args[1:])
    chat_id = update.effective_chat.id
    if chat_id not in filters_dict:
        filters_dict[chat_id] = {}
    filters_dict[chat_id][word] = reply
    await update.message.reply_text(f"✅ Filter added: {word}")

async def list_filters(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if chat_id not in filters_dict or not filters_dict[chat_id]:
        await update.message.reply_text("No filters in this group.")
        return
    text = "**Active Filters:**\n" + "\n".join(f"- `{k}`" for k in filters_dict[chat_id].keys())
    await update.message.reply_text(text, parse_mode="Markdown")

async def del_filter(update: Update, context: CallbackContext):
    if not await is_admin(update, update.effective_user.id):
        await update.message.reply_text("❌ Admin only!")
        return
    if not context.args:
        await update.message.reply_text("Usage: /delfilter <word>")
        return
    word = context.args[0].lower()
    chat_id = update.effective_chat.id
    if chat_id in filters_dict and word in filters_dict[chat_id]:
        del filters_dict[chat_id][word]
        await update.message.reply_text(f"✅ Deleted: {word}")

async def check_filters(update: Update, context: CallbackContext):
    if not update.message.text:
        return
    text = update.message.text.lower()
    chat_id = update.effective_chat.id
    if chat_id in filters_dict:
        for word, reply in filters_dict[chat_id].items():
            if word in text:
                await update.message.reply_text(reply)
                break

# ============ WELCOME ============
async def set_welcome(update: Update, context: CallbackContext):
    if not await is_admin(update, update.effective_user.id):
        await update.message.reply_text("❌ Admin only!")
        return
    if not context.args:
        await update.message.reply_text("Usage: /setwelcome <message>\nUse {user} for user's name")
        return
    welcome_msgs[update.effective_chat.id] = " ".join(context.args)
    await update.message.reply_text("✅ Welcome message set!")

async def welcome_new(update: Update, context: CallbackContext):
    for member in update.message.new_chat_members:
        if member.is_bot:
            continue
        if update.effective_chat.id in welcome_msgs:
            msg = welcome_msgs[update.effective_chat.id].format(user=member.first_name)
            await update.message.reply_text(msg)

# ============ LOCK CHECKER ============
async def check_locks(update: Update, context: CallbackContext):
    if update.effective_chat.type == "private":
        return
    if await is_admin(update, update.effective_user.id):
        return
    
    chat_data = context.chat_data
    msg = update.message
    
    if chat_data.get('locked', False):
        await msg.delete()
        return
    
    if chat_data.get('lock_links', False) and msg.entities:
        for e in msg.entities:
            if e.type == 'url':
                await msg.delete()
                await update.message.reply_text("🔒 Links are not allowed!")
                return
    
    if chat_data.get('lock_forward', False) and msg.forward_date:
        await msg.delete()
        await update.message.reply_text("🔒 Forwards are not allowed!")
        return
    
    if chat_data.get('lock_media', False) and (msg.photo or msg.video):
        await msg.delete()
        await update.message.reply_text("🔒 Media is locked!")
        return
    
    if chat_data.get('lock_voice', False) and msg.voice:
        await msg.delete()
        await update.message.reply_text("🔒 Voice messages are locked!")
        return

# ============ DM START ============
async def start(update: Update, context: CallbackContext):
    if update.effective_chat.type == "private":
        await update.message.reply_text(
            "🔥 **GAMERS ESCROW SERVICE** 🔥\n\n"
            "Group management bot by @clerkmm\n\n"
            "**Commands:**\n"
            "/panel - Open admin panel (admins only)\n"
            "/promote - Promote replied user to admin\n"
            "/demote - Demote replied admin to member\n"
            "/ban - Ban replied user\n"
            "/mute - Mute replied user\n"
            "/unmute - Unmute replied user\n"
            "/warn - Warn replied user\n"
            "/unwarn - Remove warning\n"
            "/purge - Delete messages below replied\n"
            "/filter - Add auto-reply filter\n"
            "/filters - List all filters\n"
            "/delfilter - Remove filter\n"
            "/setwelcome - Set welcome message\n"
            "/info - Get user info\n\n"
            "➕ Add me to your group:\n"
            f"https://t.me/{context.bot.username}?startgroup=add",
            parse_mode="Markdown"
        )

# ============ HELP ============
async def help_cmd(update: Update, context: CallbackContext):
    help_text = """
**📚 Bot Commands** (Admin only)

**Moderation:**
/ban - Ban replied user
/mute <minutes> - Mute replied user
/unmute - Unmute replied user
/warn - Warn replied user (3 warns = ban)
/unwarn - Remove warning
/purge - Delete all messages below replied

**Admin Management:**
/promote - Make replied user admin
/demote - Remove admin rights from replied user

**Locks:**
/lock all - Lock everything
/lock links - Lock URLs
/lock media - Lock images/videos
/lock forward - Lock forwards
/unlock all - Unlock everything

**Filters:**
/filter <word> <reply> - Add auto-reply
/filters - List all filters
/delfilter <word> - Remove filter

**Setup:**
/setwelcome <message> - Set welcome message
/info - Get user info
/panel - Open interactive admin panel

👨‍💻 **Developer:** @clerkmm
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

# ============ MAIN ============
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("panel", panel))
    app.add_handler(CommandHandler("promote", promote))
    app.add_handler(CommandHandler("demote", demote))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("warn", warn))
    app.add_handler(CommandHandler("unwarn", unwarn))
    app.add_handler(CommandHandler("purge", purge))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("filter", set_filter))
    app.add_handler(CommandHandler("filters", list_filters))
    app.add_handler(CommandHandler("delfilter", del_filter))
    app.add_handler(CommandHandler("setwelcome", set_welcome))
    
    # Callbacks & handlers
    app.add_handler(CallbackQueryHandler(menu_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_filters))
    app.add_handler(MessageHandler(filters.ALL, check_locks))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new))
    
    logger.info("Bot started!")
    app.run_polling()

if __name__ == "__main__":
    main()

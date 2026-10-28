"""Регистрация всех обработчиков бота в правильном порядке.

Группы обработки:
	-3  загрузка языка и телефона пользователя из базы;
	-2  проверка подписки на обязательную группу (останавливает обработку);
	-1  учёт нажатий кнопок;
	 0  сами сценарии: диалоги, команды, callback-кнопки, меню.
"""

from __future__ import annotations

from datetime import timedelta

from telegram import Update
from telegram.ext import (
	Application,
	CallbackQueryHandler,
	ChatMemberHandler,
	CommandHandler,
	ConversationHandler,
	MessageHandler,
	TypeHandler,
	filters,
)

from bot.config import get_feedback_chat_id, get_support_chat_id
from bot.handlers.activity import track_user_action
from bot.handlers.admin import admin_activity_panel, admin_panel, handle_admin_callback
from bot.handlers.clothing import handle_clothing_region
from bot.handlers.colony import (
	handle_application_selection,
	handle_colony_selection,
	handle_menu_text,
)
from bot.handlers.help import show_help
from bot.handlers.feedback import (
	FEEDBACK_CATEGORY,
	FEEDBACK_MESSAGE,
	cancel_feedback,
	select_feedback_category,
	send_feedback_message,
	start_feedback,
)
from bot.handlers.language import begin_language_change, select_language
from bot.handlers.lawyer import handle_lawyer_region
from bot.handlers.money_transfer import handle_money_transfer_callback
from bot.handlers.patterns import (
	CANCEL_PATTERN,
	CHANGE_LANGUAGE_PATTERN,
	FEEDBACK_BUTTON_PATTERN,
	FEEDBACK_CATEGORY_PATTERN,
	LANGUAGE_PATTERN,
	SUPPORT_BUTTON_PATTERN,
)
from bot.handlers.phone import PHONE_REQUIRED, receive_phone_number, remind_phone_required
from bot.handlers.start import handle_menu, start
from bot.handlers.subscription import (
	handle_subscription_check,
	handle_subscription_member,
	load_user_context,
	require_group_subscription,
)
from bot.handlers.support import (
	SUPPORT_MESSAGE,
	cancel_support,
	handle_support_admin_reply,
	remind_text_only,
	send_support_message,
	start_support,
)

# Незавершённый ввод обращения сбрасывается, чтобы случайный текст позже не ушёл в поддержку.
CONVERSATION_TIMEOUT = timedelta(minutes=15)

# Только новые сообщения в личном чате: отредактированное сообщение не должно
# повторно отправлять обращение или нажимать кнопку.
PRIVATE = filters.ChatType.PRIVATE & filters.UpdateType.MESSAGE
PRIVATE_TEXT = PRIVATE & filters.TEXT & ~filters.COMMAND


def _menu_fallbacks(cancel_callback) -> list:
	"""/start и /menu должны выводить из любого диалога, а не застревать в нём."""
	return [
		CommandHandler("start", start),
		CommandHandler("menu", handle_menu),
		CommandHandler("cancel", cancel_callback),
	]


def _support_conversation() -> ConversationHandler:
	return ConversationHandler(
		name="support",
		persistent=True,
		entry_points=[MessageHandler(PRIVATE_TEXT & filters.Regex(SUPPORT_BUTTON_PATTERN), start_support)],
		states={
			SUPPORT_MESSAGE: [
				MessageHandler(PRIVATE_TEXT & filters.Regex(CANCEL_PATTERN), cancel_support),
				MessageHandler(PRIVATE_TEXT, send_support_message),
				MessageHandler(PRIVATE & ~filters.COMMAND, remind_text_only),
			],
		},
		fallbacks=_menu_fallbacks(cancel_support),
		allow_reentry=True,
		conversation_timeout=CONVERSATION_TIMEOUT,
	)


def _feedback_conversation() -> ConversationHandler:
	return ConversationHandler(
		name="feedback",
		persistent=True,
		entry_points=[MessageHandler(PRIVATE_TEXT & filters.Regex(FEEDBACK_BUTTON_PATTERN), start_feedback)],
		states={
			FEEDBACK_CATEGORY: [
				MessageHandler(PRIVATE_TEXT & filters.Regex(CANCEL_PATTERN), cancel_feedback),
				MessageHandler(PRIVATE_TEXT & filters.Regex(FEEDBACK_CATEGORY_PATTERN), select_feedback_category),
				MessageHandler(PRIVATE_TEXT, select_feedback_category),
			],
			FEEDBACK_MESSAGE: [
				MessageHandler(PRIVATE_TEXT & filters.Regex(CANCEL_PATTERN), cancel_feedback),
				MessageHandler(PRIVATE_TEXT, send_feedback_message),
			],
		},
		fallbacks=_menu_fallbacks(cancel_feedback),
		allow_reentry=True,
		conversation_timeout=CONVERSATION_TIMEOUT,
	)


def _onboarding_conversation() -> ConversationHandler:
	"""Выбор языка и, если номера ещё нет, обязательная отправка телефона."""
	return ConversationHandler(
		name="onboarding",
		persistent=True,
		entry_points=[MessageHandler(PRIVATE_TEXT & filters.Regex(LANGUAGE_PATTERN), select_language)],
		states={
			PHONE_REQUIRED: [
				MessageHandler(PRIVATE & filters.CONTACT, receive_phone_number),
				MessageHandler(PRIVATE_TEXT & filters.Regex(CHANGE_LANGUAGE_PATTERN), begin_language_change),
				MessageHandler(PRIVATE & ~filters.COMMAND, remind_phone_required),
			],
		},
		fallbacks=[
			CommandHandler("start", start),
			CommandHandler("menu", handle_menu),
		],
		allow_reentry=True,
	)


def register_handlers(application: Application) -> None:
	"""Подключает все обработчики к приложению."""
	application.add_handler(TypeHandler(Update, load_user_context), group=-3)
	application.add_handler(TypeHandler(Update, require_group_subscription), group=-2)
	application.add_handler(TypeHandler(Update, track_user_action), group=-1)

	application.add_handler(
		ChatMemberHandler(handle_subscription_member, ChatMemberHandler.CHAT_MEMBER)
	)
	application.add_handler(
		MessageHandler(
			filters.Chat(chat_id=(get_support_chat_id(), get_feedback_chat_id())) & filters.REPLY,
			handle_support_admin_reply,
		)
	)

	# Диалоги регистрируются раньше команд, чтобы их fallback-и /start и /menu срабатывали внутри диалога.
	application.add_handler(_support_conversation())
	application.add_handler(_feedback_conversation())
	application.add_handler(_onboarding_conversation())

	application.add_handler(CommandHandler("start", start, filters=PRIVATE))
	application.add_handler(CommandHandler("menu", handle_menu, filters=PRIVATE))
	application.add_handler(CommandHandler("help", show_help, filters=PRIVATE))
	application.add_handler(CommandHandler("admin", admin_panel))
	application.add_handler(CommandHandler("admin2", admin_activity_panel))

	application.add_handler(CallbackQueryHandler(handle_subscription_check, pattern=r"^subscription:check$"))
	application.add_handler(CallbackQueryHandler(handle_clothing_region, pattern=r"^clothing:region:"))
	application.add_handler(CallbackQueryHandler(handle_lawyer_region, pattern=r"^lawyer:"))
	application.add_handler(CallbackQueryHandler(handle_colony_selection, pattern=r"^colonies:"))
	application.add_handler(CallbackQueryHandler(handle_application_selection, pattern=r"^application:"))
	application.add_handler(CallbackQueryHandler(handle_admin_callback, pattern=r"^admin:"))
	application.add_handler(
		CallbackQueryHandler(handle_money_transfer_callback, pattern=r"^money_transfer:(yes|no)$")
	)

	# Телефон может прийти и вне диалога: например, после приветствия при вступлении в группу.
	application.add_handler(MessageHandler(PRIVATE & filters.CONTACT, receive_phone_number))
	application.add_handler(
		MessageHandler(PRIVATE_TEXT & filters.Regex(CHANGE_LANGUAGE_PATTERN), begin_language_change)
	)
	application.add_handler(MessageHandler(PRIVATE & filters.TEXT, handle_menu_text))

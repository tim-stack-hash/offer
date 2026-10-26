"""Точка входа: собирает приложение Telegram-бота и регистрирует все обработчики."""

from __future__ import annotations

import os
import re

from dotenv import load_dotenv
from telegram import BotCommand, Update
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

from bot.config import (
	get_feedback_chat_id,
	get_lawyer_reviews_chat_id,
	get_support_chat_id,
	parse_admin_user_ids,
)
from bot.content.texts import (
	CHANGE_LANGUAGE_BUTTONS,
	CLOTHING_BUTTONS,
	LANGUAGE_BUTTONS,
	SUPPORT_BUTTON_TEXT,
)
from bot.database import initialize_user_database, update_profile_user_count
from bot.functions import (
	handle_clothing_button,
	handle_clothing_region,
	handle_lawyer_region,
)
from bot.handlers.activity import track_user_action
from bot.handlers.admin import admin_activity_panel, admin_panel, handle_admin_callback
from bot.handlers.colony import (
	handle_application_selection,
	handle_colony_selection,
	handle_location_button,
)
from bot.handlers.feedback import (
	FEEDBACK_CATEGORY,
	FEEDBACK_MESSAGE,
	cancel_feedback,
	feedback_button_pattern,
	feedback_cancel_pattern,
	feedback_category_pattern,
	select_feedback_category,
	send_feedback_message,
	start_feedback,
)
from bot.handlers.language import begin_language_change, handle_menu, select_language
from bot.handlers.money_transfer import (
	handle_money_transfer_callback,
	schedule_money_transfer_notifications,
)
from bot.handlers.phone import (
	PHONE_REQUIRED,
	receive_phone_number,
	remind_phone_required,
)
from bot.handlers.start import start
from bot.handlers.subscription import (
	handle_subscription_member,
	handle_subscription_check,
	require_group_subscription,
)
from bot.handlers.support import (
	SUPPORT_MESSAGE,
	cancel_support,
	send_support_message,
	start_support,
	handle_support_admin_reply,
	support_cancel_pattern,
)


async def set_bot_commands(application: Application) -> None:
	"""Выполняется при старте приложения: готовит базу, задаёт команды меню и счётчик в профиле."""
	initialize_user_database()
	schedule_money_transfer_notifications(application)
	await application.bot.set_my_commands(
		[
			BotCommand("start", "Запустить бота"),
			BotCommand("menu", "Выбрать язык и колонию"),
		]
	)
	await update_profile_user_count(application.bot)


def main() -> None:
	"""Читает токен и список администраторов из окружения, регистрирует обработчики и запускает polling."""
	load_dotenv()
	get_lawyer_reviews_chat_id()
	get_support_chat_id()
	get_feedback_chat_id()
	token = os.getenv("TELEGRAM_BOT_TOKEN")
	if not token:
		raise RuntimeError("Set the TELEGRAM_BOT_TOKEN environment variable")
	parse_admin_user_ids()

	application = Application.builder().token(token).post_init(set_bot_commands).build()
	application.add_handler(
		TypeHandler(Update, require_group_subscription),
		group=-2,
	)
	application.add_handler(
		ChatMemberHandler(handle_subscription_member, ChatMemberHandler.CHAT_MEMBER)
	)
	application.add_handler(CommandHandler("start", start))
	application.add_handler(
		CallbackQueryHandler(
			handle_subscription_check,
			pattern=r"^subscription:check$",
		)
	)
	application.add_handler(CommandHandler("menu", handle_menu))
	application.add_handler(CommandHandler("admin", admin_panel))
	application.add_handler(CommandHandler("admin2", admin_activity_panel))
	application.add_handler(TypeHandler(Update, track_user_action), group=-1)
	support_button_pattern = r"^(?:" + "|".join(
		re.escape(text) for text in SUPPORT_BUTTON_TEXT.values()
	) + r")$"
	application.add_handler(
		ConversationHandler(
			entry_points=[
				MessageHandler(
					filters.TEXT & filters.Regex(support_button_pattern),
					start_support,
				),
			],
			states={
				SUPPORT_MESSAGE: [
					MessageHandler(
						filters.TEXT & filters.Regex(support_button_pattern),
						start_support,
					),
					MessageHandler(
						filters.Regex(support_cancel_pattern()),
						cancel_support,
					),
					MessageHandler(filters.TEXT & ~filters.COMMAND, send_support_message),
				],
			},
			fallbacks=[
				CommandHandler("cancel", cancel_support),
			],
		)
	)
	application.add_handler(
		MessageHandler(
			filters.Chat(
				chat_id=(get_support_chat_id(), get_feedback_chat_id())
			) & filters.REPLY,
			handle_support_admin_reply,
		)
	)
	application.add_handler(
		ConversationHandler(
			entry_points=[
				MessageHandler(
					filters.TEXT & filters.Regex(feedback_button_pattern()),
					start_feedback,
				),
			],
			states={
				FEEDBACK_CATEGORY: [
					MessageHandler(
						filters.Regex(feedback_cancel_pattern()),
						cancel_feedback,
					),
					MessageHandler(
						filters.TEXT & filters.Regex(feedback_category_pattern()),
						select_feedback_category,
					),
					MessageHandler(
						filters.TEXT & ~filters.COMMAND,
						select_feedback_category,
					),
				],
				FEEDBACK_MESSAGE: [
					MessageHandler(
						filters.Regex(feedback_cancel_pattern()),
						cancel_feedback,
					),
					MessageHandler(
						filters.TEXT & ~filters.COMMAND,
						send_feedback_message,
					),
				],
			},
			fallbacks=[
				CommandHandler("cancel", cancel_feedback),
			],
		)
	)
	application.add_handler(
		CallbackQueryHandler(handle_clothing_region, pattern=r"^clothing:region:")
	)
	application.add_handler(
		CallbackQueryHandler(handle_lawyer_region, pattern=r"^lawyer:")
	)
	application.add_handler(CallbackQueryHandler(handle_colony_selection, pattern=r"^colonies:"))
	application.add_handler(
		CallbackQueryHandler(handle_application_selection, pattern=r"^application:")
	)
	application.add_handler(CallbackQueryHandler(handle_admin_callback, pattern=r"^admin:"))
	application.add_handler(
		CallbackQueryHandler(
			handle_money_transfer_callback,
			pattern=r"^money_transfer:(yes|no)$",
		)
	)
	language_texts = [label for label, _ in LANGUAGE_BUTTONS]
	language_texts.extend(("O'zbekcha", "Русский", "Узбекча"))
	language_pattern = r"^(?:" + "|".join(re.escape(text) for text in language_texts) + r")$"
	change_language_pattern = r"^(?:" + "|".join(
		re.escape(text) for text in CHANGE_LANGUAGE_BUTTONS.values()
	) + r")$"
	application.add_handler(
		MessageHandler(
			filters.TEXT & filters.Regex(change_language_pattern),
			begin_language_change,
		)
	)
	application.add_handler(
		ConversationHandler(
			entry_points=[
				MessageHandler(
					filters.TEXT & filters.Regex(language_pattern),
					select_language,
				),
			],
			states={
				PHONE_REQUIRED: [
					MessageHandler(filters.CONTACT, receive_phone_number),
					MessageHandler(filters.TEXT, remind_phone_required),
				],
			},
			fallbacks=[],
		)
	)
	clothing_texts = [
		CLOTHING_BUTTONS.get(language, CLOTHING_BUTTONS["ru"])
		for language in ("ru", "uz", "uz_cyr")
	]
	clothing_pattern = r"^(?:" + "|".join(
		re.escape(text) for text in clothing_texts
	) + r")$"
	application.add_handler(
		MessageHandler(
			filters.TEXT & filters.Regex(clothing_pattern),
			handle_clothing_button,
		)
	)
	application.add_handler(MessageHandler(filters.TEXT, handle_location_button))
	application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
	main()

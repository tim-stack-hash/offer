"""Команда /help: коротко о том, что умеет бот и где что находится."""

from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from bot.content.texts import (
	COLONY_GROUP_BUTTONS,
	FEEDBACK_BUTTON_TEXT,
	HELP_TEXTS,
	MAIN_GROUP_BUTTONS,
	SUPPORT_BUTTON_TEXT,
)
from bot.handlers.common import HTML, bold, escape, return_user_keyboard, user_language
from bot.keyboards import MENU_SECTION_BUTTONS


def help_text(language: str) -> str:
	"""Справка с настоящими названиями кнопок на языке пользователя (HTML)."""
	texts = HELP_TEXTS.get(language, HELP_TEXTS["ru"])
	info_section, services_section, _ = MENU_SECTION_BUTTONS.get(language, MENU_SECTION_BUTTONS["ru"])

	def button(labels: dict[str, str]) -> str:
		return labels.get(language, labels["ru"])

	def item(label: str, description: str) -> str:
		return f"{bold(label)} — {escape(description)}"

	return "\n".join(
		[
			texts["title"],
			"",
			escape(texts["menu"]),
			item(info_section, texts["info"]),
			item(services_section, texts["services"]),
			"",
			item(button(COLONY_GROUP_BUTTONS), texts["colony_group"]),
			item(button(MAIN_GROUP_BUTTONS), texts["main_group"]),
			item(button(SUPPORT_BUTTON_TEXT), texts["support"]),
			item(button(FEEDBACK_BUTTON_TEXT), texts["feedback"]),
			"",
			escape(texts["commands"]),
		]
	)


async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	message = update.effective_message
	if not message:
		return

	await message.reply_text(
		help_text(user_language(context)),
		parse_mode=HTML,
		reply_markup=return_user_keyboard(context),
	)

"""Обработка callback-кнопок выбора колонии (инлайн-клавиатура списка колоний)."""

from __future__ import annotations

from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.content.colonies import COLONY_COORDINATES, COLONY_GROUP_LABELS, COLONY_GROUPS
from bot.content.texts import (
	COLONY_NOT_FOUND_TEXTS,
	COLONY_PROMPTS,
	COLONY_SELECTED_TEXTS,
	colony_location_prompt,
)
from bot.handlers.common import (
	HTML,
	bold,
	escape,
	menu_screen,
	no_data_text,
	selected_colony_name,
	user_language,
)
from bot.keyboards import colony_group_keyboard


async def handle_colony_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Обрабатывает callback-кнопки колоний: открытие списка, показ локации, выбор конкретной колонии."""
	query = update.callback_query
	if not query or not query.data:
		return

	language = user_language(context)
	if query.data == "colonies:open":
		await query.answer()
		if query.message:
			await query.edit_message_text(
				COLONY_PROMPTS.get(language, COLONY_PROMPTS["ru"]),
				reply_markup=colony_group_keyboard(language),
			)
		return

	if query.data == "colonies:location":
		coordinates = COLONY_COORDINATES.get(context.user_data.get("colony"))
		if not coordinates:
			await query.answer(no_data_text(language), show_alert=True)
			return
		await query.answer()
		if query.message:
			colony_name = selected_colony_name(context, language).removeprefix("📍").strip()
			await query.message.reply_text(colony_location_prompt(language, colony_name))
			await query.message.reply_location(latitude=coordinates[0], longitude=coordinates[1])
		return

	try:
		prefix, action, index_text = query.data.split(":", 2)
		colony_index = int(index_text)
		if prefix != "colonies" or action != "select":
			return
		colony_group = COLONY_GROUPS[colony_index]
	except (ValueError, IndexError):
		await query.answer(
			COLONY_NOT_FOUND_TEXTS.get(language, COLONY_NOT_FOUND_TEXTS["ru"]),
			show_alert=True,
		)
		return

	context.user_data["colony"] = colony_group
	context.user_data["menu_section"] = "root"
	colony_name = COLONY_GROUP_LABELS.get(language, COLONY_GROUP_LABELS["ru"])[colony_index]
	context.user_data["colony_name"] = colony_name
	await query.answer()
	if not query.message:
		return

	selected_text = COLONY_SELECTED_TEXTS.get(language, COLONY_SELECTED_TEXTS["ru"])
	await query.edit_message_text(
		f"{escape(selected_text)} {bold(colony_name)}",
		parse_mode=HTML,
		reply_markup=InlineKeyboardMarkup([]),
	)
	menu_text, keyboard = menu_screen(context)
	await query.message.reply_text(menu_text, parse_mode=HTML, reply_markup=keyboard)

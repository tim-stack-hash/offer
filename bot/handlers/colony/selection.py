"""Обработка callback-кнопок выбора колонии (инлайн-клавиатура списка колоний)."""

from __future__ import annotations

from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.content.colonies import COLONY_COORDINATES, COLONY_GROUP_LABELS, COLONY_GROUPS
from bot.content.texts import (
	ACTION_PROMPTS,
	COLONY_PROMPTS,
	COLONY_SELECTED_TEXTS,
	LOCATION_MISSING_TEXTS,
	colony_location_prompt,
)
from bot.handlers.common import user_language
from bot.keyboards import (
	colony_group_keyboard,
	colony_location_reply_keyboard,
	language_selection_keyboard,
)


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
		colony_group = context.user_data.get("colony")
		coordinates = COLONY_COORDINATES.get(colony_group)
		if not coordinates:
			await query.answer(
				LOCATION_MISSING_TEXTS.get(language, LOCATION_MISSING_TEXTS["ru"]),
				show_alert=True,
			)
			return
		await query.answer()
		if query.message:
			colony_name = (
				context.user_data.get("colony_name") or colony_group
			).removeprefix("📍").strip()
			await query.message.reply_text(
				colony_location_prompt(language, colony_name)
			)
			await query.message.reply_location(
				latitude=coordinates[0],
				longitude=coordinates[1],
			)
		return

	try:
		prefix, action, index_text = query.data.split(":", 2)
		colony_index = int(index_text)
		if prefix != "colonies" or action != "select":
			return
		colony_group = COLONY_GROUPS[colony_index]
	except (ValueError, IndexError):
		not_found_texts = {
			"ru": "Колония не найдена.",
			"uz": "Koloniya topilmadi.",
			"uz_cyr": "Колония топилмади.",
		}
		await query.answer(not_found_texts.get(language, not_found_texts["ru"]), show_alert=True)
		return

	context.user_data["colony"] = colony_group
	context.user_data["menu_section"] = "root"
	colony_name = COLONY_GROUP_LABELS.get(language, COLONY_GROUP_LABELS["ru"])[colony_index]
	context.user_data["colony_name"] = colony_name
	await query.answer()
	if query.message:
		selected_text = COLONY_SELECTED_TEXTS.get(language, COLONY_SELECTED_TEXTS["ru"])
		await query.edit_message_text(
			f"{selected_text}\n{colony_name}",
			reply_markup=InlineKeyboardMarkup([]),
		)
		location_keyboard = colony_location_reply_keyboard(language, colony_group)
		if not location_keyboard:
			await query.message.reply_text(
				LOCATION_MISSING_TEXTS.get(language, LOCATION_MISSING_TEXTS["ru"]),
				reply_markup=language_selection_keyboard(),
			)
			return
		await query.message.reply_text(
			ACTION_PROMPTS.get(language, ACTION_PROMPTS["ru"]),
			reply_markup=location_keyboard,
		)

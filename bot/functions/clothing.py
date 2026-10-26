"""Функции сценария выбора региона и продавца одежды."""

from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from bot.content.clothing_regions import CLOTHING_REGIONS
from bot.content.texts import (
	CLOTHING_BUTTONS,
	CLOTHING_REGION_NOT_FOUND_TEXTS,
	CLOTHING_REGION_PROMPTS,
	CLOTHING_SELLER_PROMPTS,
)
from bot.keyboards import clothing_regions_keyboard, clothing_sellers_keyboard


async def handle_clothing_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Открывает выбор региона при нажатии кнопки «Одежда»."""
	message = update.message
	if not message or not message.text:
		return

	language = context.user_data.get("language", "ru")
	button_text = CLOTHING_BUTTONS.get(language, CLOTHING_BUTTONS["ru"])
	if message.text.strip() != button_text:
		return

	context.user_data.pop("clothing_region", None)
	await message.reply_text(
		CLOTHING_REGION_PROMPTS.get(language, CLOTHING_REGION_PROMPTS["ru"]),
		reply_markup=clothing_regions_keyboard(language),
	)


async def handle_clothing_region(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""После выбора региона показывает продавца, ведущего в Telegram-группу."""
	query = update.callback_query
	if not query or not query.data:
		return

	language = context.user_data.get("language", "ru")
	region_id = query.data.removeprefix("clothing:region:")
	region_names = CLOTHING_REGIONS.get(region_id)
	if not region_names:
		await query.answer(
			CLOTHING_REGION_NOT_FOUND_TEXTS.get(
				language,
				CLOTHING_REGION_NOT_FOUND_TEXTS["ru"],
			),
			show_alert=True,
		)
		return

	context.user_data["clothing_region"] = region_id
	await query.answer()
	if query.message:
		region_name = region_names.get(language, region_names["ru"])
		seller_prompt = CLOTHING_SELLER_PROMPTS.get(
			language,
			CLOTHING_SELLER_PROMPTS["ru"],
		).format(region=region_name)
		await query.edit_message_text(
			seller_prompt,
			reply_markup=clothing_sellers_keyboard(language),
		)

"""Инлайн-клавиатуры выбора региона и продавца одежды."""

from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.config import CLOTHING_LINK_URL
from bot.content.clothing_regions import CLOTHING_REGIONS
from bot.content.texts import CLOTHING_SELLER_BUTTONS


def clothing_regions_keyboard(language: str) -> InlineKeyboardMarkup:
	"""Показывает регионы одежды и прямую ссылку на образцы в двух колонках."""
	buttons = [
		InlineKeyboardButton(
			region_names.get(language, region_names["ru"]),
			url=CLOTHING_LINK_URL,
		)
		if region_id == "clothing"
		else InlineKeyboardButton(
			region_names.get(language, region_names["ru"]),
			callback_data=f"clothing:region:{region_id}",
		)
		for region_id, region_names in CLOTHING_REGIONS.items()
	]
	return InlineKeyboardMarkup(
		[
			buttons[row_start:row_start + 2]
			for row_start in range(0, len(buttons), 2)
		]
	)


def clothing_sellers_keyboard(language: str) -> InlineKeyboardMarkup:
	"""Показывает продавца и ссылку на группу с одеждой."""
	button_text = CLOTHING_SELLER_BUTTONS.get(
		language,
		CLOTHING_SELLER_BUTTONS["ru"],
	)
	return InlineKeyboardMarkup(
		[[InlineKeyboardButton(button_text, url=CLOTHING_LINK_URL)]]
	)

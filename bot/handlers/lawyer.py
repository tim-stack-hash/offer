"""Сценарий выбора адвоката, звонка и отзывов."""

from __future__ import annotations

import logging
import sqlite3

from telegram import ForceReply, InlineKeyboardMarkup, MessageEntity, Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from bot.config import get_lawyer_reviews_chat_id
from bot.content.lawyer_regions import LAWYER_REGIONS
from bot.content.lawyers import LAWYERS
from bot.content.texts import (
	LAWYER_NOT_FOUND_TEXTS,
	LAWYER_PHOTO_MISSING_TEXTS,
	LAWYER_PROFILE_CAPTIONS,
	LAWYER_PROMPTS,
	LAWYER_CALL_PROMPTS,
	LAWYER_REVIEW_EMPTY_TEXTS,
	LAWYER_REVIEW_AUTHOR_LABELS,
	LAWYER_REVIEW_LIST_HEADERS,
	LAWYER_REVIEW_MENU_PROMPTS,
	LAWYER_REVIEW_PROMPTS,
	LAWYER_REVIEW_PUBLISH_ERROR_TEXTS,
	LAWYER_REVIEW_READ_ERROR_TEXTS,
	LAWYER_REVIEW_SAVE_ERROR_TEXTS,
	LAWYER_REVIEW_SUCCESS_TEXTS,
	LAWYER_REVIEW_TOO_LONG_TEXTS,
	LAWYER_REGION_NOT_FOUND_TEXTS,
	LAWYER_REGION_PROMPTS,
	UNKNOWN_ACTION_TEXTS,
)
from bot.database import (
	get_lawyer_review_count,
	get_lawyer_reviews,
	save_lawyer_review,
)
from bot.handlers.common import HTML, escape, no_data_card, telegram_text_length, user_language
from bot.handlers.patterns import BUTTON_LABELS
from bot.keyboards import (
	lawyer_profile_keyboard,
	lawyer_review_menu_keyboard,
	lawyer_regions_keyboard,
	lawyers_by_region_keyboard,
)

LOGGER = logging.getLogger(__name__)
MAX_LAWYER_REVIEW_LENGTH = 3000
MAX_TELEGRAM_MESSAGE_LENGTH = 4096


async def handle_lawyer_region(
	update: Update,
	context: ContextTypes.DEFAULT_TYPE,
) -> None:
	"""Обрабатывает выбор региона, карточки адвоката и действия с отзывами."""
	query = update.callback_query
	if not query or not query.data:
		return

	language = user_language(context)
	parts = query.data.split(":", 2)
	if len(parts) != 3 or parts[0] != "lawyer":
		await query.answer(UNKNOWN_ACTION_TEXTS.get(language, UNKNOWN_ACTION_TEXTS["ru"]), show_alert=True)
		return

	_, action, item_id = parts
	message = query.message

	if action == "region":
		region_names = LAWYER_REGIONS.get(item_id)
		if not region_names:
			await query.answer(
				LAWYER_REGION_NOT_FOUND_TEXTS.get(
					language,
					LAWYER_REGION_NOT_FOUND_TEXTS["ru"],
				),
				show_alert=True,
			)
			return

		context.user_data["lawyer_region"] = item_id
		await query.answer()
		if not message:
			return

		region_name = region_names.get(language, region_names["ru"])
		lawyer_keyboard = lawyers_by_region_keyboard(item_id)
		if not lawyer_keyboard.inline_keyboard:
			await message.edit_text(
				no_data_card(language, f"⚖️ {region_name}"),
				parse_mode=HTML,
				reply_markup=InlineKeyboardMarkup([]),
			)
			return

		prompt = LAWYER_PROMPTS.get(
			language,
			LAWYER_PROMPTS["ru"],
		).format(region=region_name)
		await message.edit_text(prompt, reply_markup=lawyer_keyboard)
		return

	lawyer = LAWYERS.get(item_id)
	if not lawyer:
		await query.answer(LAWYER_NOT_FOUND_TEXTS.get(language, LAWYER_NOT_FOUND_TEXTS["ru"]), show_alert=True)
		return

	if action == "profile":
		context.user_data["lawyer_id"] = item_id
		await query.answer()
		if not message:
			return

		language_region_names = LAWYER_REGIONS[lawyer["region"]]
		try:
			review_count = get_lawyer_review_count(item_id)
		except sqlite3.Error:
			LOGGER.exception("Could not count reviews for lawyer %s", item_id)
			await message.reply_text(
				LAWYER_REVIEW_READ_ERROR_TEXTS.get(
					language,
					LAWYER_REVIEW_READ_ERROR_TEXTS["ru"],
				)
			)
			return

		caption = LAWYER_PROFILE_CAPTIONS.get(
			language,
			LAWYER_PROFILE_CAPTIONS["ru"],
		).format(
			name=escape(lawyer["name"]),
			region=escape(language_region_names.get(language, language_region_names["ru"])),
			review_count=review_count,
		)
		try:
			with open(lawyer["photo_path"], "rb") as photo:
				await message.reply_photo(
					photo=photo,
					caption=caption,
					parse_mode=HTML,
					reply_markup=lawyer_profile_keyboard(language, item_id),
				)
		except OSError:
			LOGGER.warning("Lawyer profile photo is missing: %s", lawyer["photo_path"])
			photo_missing = LAWYER_PHOTO_MISSING_TEXTS.get(language, LAWYER_PHOTO_MISSING_TEXTS["ru"])
			await message.reply_text(
				f"{caption}\n\n{escape(photo_missing)}",
				parse_mode=HTML,
				reply_markup=lawyer_profile_keyboard(language, item_id),
			)
		return

	if action == "reviews":
		await query.answer()
		if message:
			await message.reply_text(
				LAWYER_REVIEW_MENU_PROMPTS.get(
					language,
					LAWYER_REVIEW_MENU_PROMPTS["ru"],
				),
				reply_markup=lawyer_review_menu_keyboard(language, item_id),
			)
		return

	if action == "call":
		await query.answer()
		if message:
			await message.reply_text(
				LAWYER_CALL_PROMPTS.get(
					language,
					LAWYER_CALL_PROMPTS["ru"],
				)
			)
			phone_number = lawyer["phone_number"]
			await message.reply_text(
				phone_number,
				entities=[
					MessageEntity(
						type=MessageEntity.PHONE_NUMBER,
						offset=0,
						length=len(phone_number),
					)
				],
			)
		return

	if action == "write_review":
		context.user_data["pending_lawyer_review"] = item_id
		await query.answer()
		if message:
			prompt = LAWYER_REVIEW_PROMPTS.get(
				language,
				LAWYER_REVIEW_PROMPTS["ru"],
			).format(name=lawyer["name"])
			await message.reply_text(
				prompt,
				reply_markup=ForceReply(selective=True),
			)
		return

	if action == "show_reviews":
		await query.answer()
		if not message:
			return

		try:
			reviews = get_lawyer_reviews(item_id)
		except sqlite3.Error:
			LOGGER.exception("Could not read reviews for lawyer %s", item_id)
			await message.reply_text(
				LAWYER_REVIEW_READ_ERROR_TEXTS.get(
					language,
					LAWYER_REVIEW_READ_ERROR_TEXTS["ru"],
				)
			)
			return
		if not reviews:
			await message.reply_text(
				LAWYER_REVIEW_EMPTY_TEXTS.get(
					language,
					LAWYER_REVIEW_EMPTY_TEXTS["ru"],
				)
			)
			return

		header = LAWYER_REVIEW_LIST_HEADERS.get(
			language,
			LAWYER_REVIEW_LIST_HEADERS["ru"],
		).format(name=lawyer["name"])
		current_text = header
		author_label = LAWYER_REVIEW_AUTHOR_LABELS.get(
			language,
			LAWYER_REVIEW_AUTHOR_LABELS["ru"],
		)
		for index, (review_text, created_at, author) in enumerate(reviews, start=1):
			review_block = (
				f"\n\n{index}. {created_at}\n"
				f"👤 {author_label}: {author}\n{review_text}"
			)
			if (
				telegram_text_length(current_text)
				+ telegram_text_length(review_block)
				> MAX_TELEGRAM_MESSAGE_LENGTH
			):
				await message.reply_text(current_text)
				current_text = header
			current_text += review_block
		await message.reply_text(current_text)
		return

	await query.answer(UNKNOWN_ACTION_TEXTS.get(language, UNKNOWN_ACTION_TEXTS["ru"]), show_alert=True)


async def handle_lawyer_button(
	update: Update,
	context: ContextTypes.DEFAULT_TYPE,
) -> None:
	"""Открывает список регионов при нажатии кнопки «Адвокаты»."""
	message = update.message
	if not message:
		return

	language = user_language(context)
	context.user_data.pop("lawyer_region", None)
	context.user_data.pop("lawyer_id", None)
	context.user_data.pop("pending_lawyer_review", None)
	await message.reply_text(
		LAWYER_REGION_PROMPTS.get(language, LAWYER_REGION_PROMPTS["ru"]),
		reply_markup=lawyer_regions_keyboard(language),
	)


async def handle_lawyer_review_text(
	update: Update,
	context: ContextTypes.DEFAULT_TYPE,
) -> bool:
	"""Сохраняет отзыв, ожидаемый после нажатия кнопки «Оставить отзыв»."""
	lawyer_id = context.user_data.get("pending_lawyer_review")
	message = update.message
	if not lawyer_id or not message or not message.text:
		return False

	review_text = message.text.strip()
	if review_text in BUTTON_LABELS:
		# Пользователь передумал и нажал кнопку меню — это не текст отзыва.
		context.user_data.pop("pending_lawyer_review", None)
		return False

	language = user_language(context)
	lawyer = LAWYERS.get(lawyer_id)
	if not lawyer:
		context.user_data.pop("pending_lawyer_review", None)
		await message.reply_text(LAWYER_NOT_FOUND_TEXTS.get(language, LAWYER_NOT_FOUND_TEXTS["ru"]))
		return True

	if not review_text:
		await message.reply_text(
			LAWYER_REVIEW_PROMPTS.get(
				language,
				LAWYER_REVIEW_PROMPTS["ru"],
			).format(name=lawyer["name"])
		)
		return True
	if telegram_text_length(review_text) > MAX_LAWYER_REVIEW_LENGTH:
		await message.reply_text(
			LAWYER_REVIEW_TOO_LONG_TEXTS.get(
				language,
				LAWYER_REVIEW_TOO_LONG_TEXTS["ru"],
			)
		)
		return True

	user = update.effective_user
	if not user:
		return False

	try:
		save_lawyer_review(lawyer_id, user.id, review_text)
	except sqlite3.Error:
		LOGGER.exception("Could not save review for lawyer %s", lawyer_id)
		await message.reply_text(
			LAWYER_REVIEW_SAVE_ERROR_TEXTS.get(
				language,
				LAWYER_REVIEW_SAVE_ERROR_TEXTS["ru"],
			)
		)
		return True

	context.user_data.pop("pending_lawyer_review", None)
	author = user.full_name
	if user.username:
		author = f"{author} (@{user.username})" if author else f"@{user.username}"
	if not author:
		author = f"ID {user.id}"
	channel_text = (
		f"⭐ Отзыв об адвокате {lawyer['name']}\n"
		f"👤 Автор: {author}\n\n{review_text}"
	)
	channel_id = get_lawyer_reviews_chat_id()
	try:
		await context.bot.send_message(
			chat_id=channel_id,
			text=channel_text,
		)
	except TelegramError:
		LOGGER.exception(
			"Could not publish review for lawyer %s to channel %s",
			lawyer_id,
			channel_id,
		)
		await message.reply_text(
			LAWYER_REVIEW_PUBLISH_ERROR_TEXTS.get(
				language,
				LAWYER_REVIEW_PUBLISH_ERROR_TEXTS["ru"],
			)
		)
		return True

	await message.reply_text(
		LAWYER_REVIEW_SUCCESS_TEXTS.get(
			language,
			LAWYER_REVIEW_SUCCESS_TEXTS["ru"],
		)
	)
	return True

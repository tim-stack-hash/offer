"""Выбор и смена языка интерфейса."""

from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.content.colonies import COLONY_GROUPS
from bot.content.texts import (
	CHANGE_LANGUAGE_PROMPTS,
	COLONY_PROMPTS,
	LANGUAGE_SELECTED_TEXTS,
	PHONE_PROMPTS,
)
from bot.database import register_user, save_user_language
from bot.handlers.common import HTML, escape, menu_screen, step_header, user_language
from bot.handlers.patterns import language_by_label
from bot.handlers.phone import PHONE_REQUIRED
from bot.handlers.subscription import is_group_member, prompt_group_subscription
from bot.keyboards import (
	change_language_keyboard,
	colony_group_keyboard,
	contact_request_keyboard,
	language_selection_keyboard,
)


async def begin_language_change(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Кнопка «Поменять язык»: показывает выбор языка, сохраняя текущий шаг сценария."""
	if not update.message:
		return

	context.user_data["changing_language"] = True
	language = user_language(context)
	await update.message.reply_text(
		CHANGE_LANGUAGE_PROMPTS.get(language, CHANGE_LANGUAGE_PROMPTS["ru"]),
		reply_markup=language_selection_keyboard(),
	)


async def select_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	"""Сохраняет язык и продолжает сценарий с того места, где пользователь остановился."""
	message = update.message
	user = update.effective_user
	if not message or not message.text or not user:
		return ConversationHandler.END

	language = language_by_label(message.text)
	if language is None:
		return ConversationHandler.END

	changing_language = context.user_data.pop("changing_language", False)
	context.user_data["language"] = language
	register_user(user.id, user.username, user.first_name, user.last_name)
	save_user_language(user.id, language)

	if not await is_group_member(update, context):
		await prompt_group_subscription(update, context)
		return ConversationHandler.END

	selected_text = escape(LANGUAGE_SELECTED_TEXTS[language])
	if changing_language and context.user_data.get("colony") in COLONY_GROUPS:
		# Язык меняли внутри меню колонии — возвращаем пользователя в тот же раздел.
		menu_text, keyboard = menu_screen(context, context.user_data.get("menu_section", "root"))
		await message.reply_text(f"{selected_text}\n\n{menu_text}", parse_mode=HTML, reply_markup=keyboard)
		return ConversationHandler.END

	if context.user_data.get("phone_number"):
		await message.reply_text(
			LANGUAGE_SELECTED_TEXTS[language],
			reply_markup=change_language_keyboard(language),
		)
		await message.reply_text(
			COLONY_PROMPTS.get(language, COLONY_PROMPTS["ru"]),
			reply_markup=colony_group_keyboard(language),
		)
		return ConversationHandler.END

	phone_prompt = escape(PHONE_PROMPTS.get(language, PHONE_PROMPTS["ru"])["prompt"])
	await message.reply_text(
		f"{selected_text}\n\n{step_header(language, 2)}\n{phone_prompt}",
		parse_mode=HTML,
		reply_markup=contact_request_keyboard(language),
	)
	return PHONE_REQUIRED

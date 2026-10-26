"""Выбор и смена языка интерфейса, команда /menu."""

from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.content.colonies import COLONY_GROUPS, COLONY_GROUP_LABELS
from bot.content.texts import (
	ACTION_PROMPTS,
	COLONY_PROMPTS,
	COLONY_SELECTED_TEXTS,
	LANGUAGE_BUTTONS,
	PHONE_PROMPTS,
)
from bot.database import get_user_phone_number, save_user_language
from bot.handlers.phone import PHONE_REQUIRED
from bot.handlers.subscription import is_group_member, prompt_group_subscription
from bot.keyboards import (
	change_language_keyboard,
	colony_group_keyboard,
	colony_location_reply_keyboard,
	contact_request_keyboard,
	language_selection_keyboard,
)


async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Команда /menu: сбрасывает сохранённые данные пользователя и возвращает к выбору языка."""
	message = update.effective_message
	if not message:
		return

	if update.callback_query:
		await update.callback_query.answer()
	context.user_data.clear()
	await message.reply_text(
		"🌐 Выберите язык / Tilni tanlang:",
		reply_markup=language_selection_keyboard(),
	)


async def begin_language_change(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Нажатие кнопки «Поменять язык»: запоминает намерение и показывает выбор языка."""
	if not update.message:
		return

	context.user_data["changing_language"] = True
	language = context.user_data.get("language", "ru")
	prompts = {
		"ru": "🌐 Выберите новый язык:",
		"uz": "🌐 Yangi tilni tanlang:",
		"uz_cyr": "🌐 Янги тилни танланг:",
	}
	await update.message.reply_text(
		prompts.get(language, prompts["ru"]),
		reply_markup=language_selection_keyboard(),
	)


async def select_language(
	update: Update,
	context: ContextTypes.DEFAULT_TYPE,
) -> int:
	"""Обрабатывает выбор языка и возвращает пользователя туда, где он остановился в сценарии."""
	if not update.message or not update.message.text:
		return ConversationHandler.END

	language = dict(LANGUAGE_BUTTONS).get(update.message.text)
	if language is None:
		language = {"O'zbekcha": "uz", "Русский": "ru", "Узбекча": "uz_cyr"}.get(update.message.text)
	if language is None:
		return ConversationHandler.END
	changing_language = context.user_data.pop("changing_language", False)
	context.user_data["language"] = language
	user = update.effective_user
	if user:
		save_user_language(user.id, language)
		if not await is_group_member(update, context):
			await prompt_group_subscription(update, context)
			return ConversationHandler.END
	if user and not context.user_data.get("phone_number"):
		phone_number = get_user_phone_number(user.id)
		if phone_number:
			context.user_data["phone_number"] = phone_number
	selected_texts = {
		"uz": "🇺🇿 O'zbek tili tanlandi.",
		"ru": "🇷🇺 Вы выбрали русский язык.",
		"uz_cyr": "🇺🇿 Ўзбек тили танланди.",
	}
	await update.message.reply_text(
		selected_texts[language],
		reply_markup=change_language_keyboard(language),
	)

	if changing_language:
		# Пользователь менял язык, а не выбирал его впервые — продолжаем с того же шага сценария.
		colony_group = context.user_data.get("colony")
		if colony_group in COLONY_GROUPS:
			colony_index = COLONY_GROUPS.index(colony_group)
			colony_name = COLONY_GROUP_LABELS[language][colony_index]
			context.user_data["colony_name"] = colony_name
			selected_text = COLONY_SELECTED_TEXTS[language]
			await update.message.reply_text(
				f"{selected_text}\n{colony_name}",
			)
			await update.message.reply_text(
				ACTION_PROMPTS.get(language, ACTION_PROMPTS["ru"]),
				reply_markup=colony_location_reply_keyboard(
					language,
					colony_group,
					context.user_data.get("menu_section", "root"),
				),
			)
			return ConversationHandler.END

		if context.user_data.get("phone_number"):
			await update.message.reply_text(
				COLONY_PROMPTS.get(language, COLONY_PROMPTS["ru"]),
				reply_markup=colony_group_keyboard(language),
			)
			return ConversationHandler.END

	if context.user_data.get("phone_number"):
		await update.message.reply_text(
			COLONY_PROMPTS.get(language, COLONY_PROMPTS["ru"]),
			reply_markup=colony_group_keyboard(language),
		)
		return ConversationHandler.END

	await update.message.reply_text(
		PHONE_PROMPTS.get(language, PHONE_PROMPTS["ru"])["prompt"],
		reply_markup=contact_request_keyboard(language),
	)
	return PHONE_REQUIRED

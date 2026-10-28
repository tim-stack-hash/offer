"""Выбор и смена языка интерфейса."""

from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.content.colonies import COLONY_GROUPS, COLONY_GROUP_LABELS
from bot.content.texts import (
	ACTION_PROMPTS,
	COLONY_PROMPTS,
	COLONY_SELECTED_TEXTS,
	PHONE_PROMPTS,
)
from bot.database import register_user, save_user_language
from bot.handlers.common import user_language
from bot.handlers.patterns import language_by_label
from bot.handlers.phone import PHONE_REQUIRED
from bot.handlers.subscription import is_group_member, prompt_group_subscription
from bot.keyboards import (
	change_language_keyboard,
	colony_group_keyboard,
	colony_location_reply_keyboard,
	contact_request_keyboard,
	language_selection_keyboard,
)

CHANGE_LANGUAGE_PROMPTS = {
	"ru": "🌐 Выберите новый язык:",
	"uz": "🌐 Yangi tilni tanlang:",
	"uz_cyr": "🌐 Янги тилни танланг:",
}

LANGUAGE_SELECTED_TEXTS = {
	"uz": "🇺🇿 O'zbek tili tanlandi.",
	"ru": "🇷🇺 Вы выбрали русский язык.",
	"uz_cyr": "🇺🇿 Ўзбек тили танланди.",
}


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

	await message.reply_text(
		LANGUAGE_SELECTED_TEXTS[language],
		reply_markup=change_language_keyboard(language),
	)

	colony_group = context.user_data.get("colony")
	if changing_language and colony_group in COLONY_GROUPS:
		# Пользователь менял язык внутри меню колонии — возвращаем его в то же меню.
		colony_name = COLONY_GROUP_LABELS[language][COLONY_GROUPS.index(colony_group)]
		context.user_data["colony_name"] = colony_name
		await message.reply_text(f"{COLONY_SELECTED_TEXTS[language]}\n{colony_name}")
		await message.reply_text(
			ACTION_PROMPTS.get(language, ACTION_PROMPTS["ru"]),
			reply_markup=colony_location_reply_keyboard(
				language,
				colony_group,
				context.user_data.get("menu_section", "root"),
			),
		)
		return ConversationHandler.END

	if context.user_data.get("phone_number"):
		await message.reply_text(
			COLONY_PROMPTS.get(language, COLONY_PROMPTS["ru"]),
			reply_markup=colony_group_keyboard(language),
		)
		return ConversationHandler.END

	await message.reply_text(
		PHONE_PROMPTS.get(language, PHONE_PROMPTS["ru"])["prompt"],
		reply_markup=contact_request_keyboard(language),
	)
	return PHONE_REQUIRED

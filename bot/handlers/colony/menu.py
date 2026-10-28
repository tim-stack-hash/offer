"""Reply-меню: разделы, информация о выбранной колонии и услуги.

Подпись каждой кнопки на любом языке сопоставляется с действием, поэтому кнопки
продолжают работать, даже если у пользователя осталась клавиатура на другом
языке. Действиям, которым нужна колония, без неё бот предлагает её выбрать.
Если по кнопке нет информации, бот отвечает «Данных нет».
"""

from __future__ import annotations

import os
import re
from collections.abc import Awaitable, Callable, Iterable
from functools import partial

from telegram import Update
from telegram.ext import ContextTypes

from bot.config import (
	ADDITIONAL_INFO_IMAGE_PATHS,
	ADDITIONAL_INFO_INTRO_IMAGE_PATHS,
	APPLICATION_IMAGE_PATHS,
	COLONY_REGIME_IMAGE_PATHS,
	SUPPORTED_LANGUAGES,
)
from bot.content.colonies import COLONY_COORDINATES, COLONY_GROUPS, HOTEL_INFO, colony_directory_text
from bot.content.texts import (
	ADDITIONAL_INFO_BUTTONS,
	ADDITIONAL_INFO_COLONY_NUMBERS_TEXTS,
	ADDITIONAL_INFO_LIST_TEXTS,
	APPLICATION_TYPE_PROMPTS,
	CHANGE_COLONY_BUTTONS,
	CLOTHING_BUTTONS,
	COLONY_APPLICATION_BUTTONS,
	COLONY_DIRECTORY_BUTTONS,
	COLONY_GROUP_BUTTONS,
	COLONY_GROUP_LINK_PROMPTS,
	COLONY_LOCATION_BUTTONS,
	COLONY_PROMPTS,
	GROUP_SELECTED_TEXTS,
	HOTEL_CARD_TEXTS,
	MAIN_GROUP_BUTTONS,
	MAIN_GROUP_LINK_PROMPTS,
	NO_DATA_TEXTS,
	PHONE_PROMPTS,
	UNKNOWN_ACTION_TEXTS,
	UNKNOWN_TEXT_REPLIES,
	colony_action_button_texts,
	colony_location_prompt,
)
from bot.handlers.clothing import handle_clothing_button
from bot.handlers.common import (
	HTML,
	bold,
	escape,
	menu_screen,
	no_data_card,
	no_data_text,
	return_user_keyboard,
	selected_colony_name,
	step_header,
	user_language,
)
from bot.handlers.lawyer import handle_lawyer_button, handle_lawyer_review_text
from bot.handlers.money_transfer import handle_money_transfer_button
from bot.keyboards import (
	MENU_SECTION_BUTTONS,
	application_type_keyboard,
	colony_group_keyboard,
	colony_group_link_keyboard,
	contact_request_keyboard,
	main_group_link_keyboard,
)
from bot.services.media import send_cached_media, send_cached_photo_album

MenuAction = Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[None]]


async def _ask_colony(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	language = user_language(context)
	await update.message.reply_text(
		COLONY_PROMPTS.get(language, COLONY_PROMPTS["ru"]),
		reply_markup=colony_group_keyboard(language),
	)


async def _resume_onboarding(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Настройка не завершена (например, после обновления бота) — продолжаем с нужного шага."""
	if context.user_data.get("phone_number"):
		await _ask_colony(update, context)
		return

	language = user_language(context)
	phone_prompt = escape(PHONE_PROMPTS.get(language, PHONE_PROMPTS["ru"])["prompt"])
	await update.message.reply_text(
		f"{step_header(language, 2)}\n{phone_prompt}",
		parse_mode=HTML,
		reply_markup=contact_request_keyboard(language),
	)


async def _reply_unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Непонятный текст: подсказываем, что делать дальше, и возвращаем нужную клавиатуру."""
	if not context.user_data.get("phone_number") or context.user_data.get("colony") not in COLONY_GROUPS:
		await _resume_onboarding(update, context)
		return

	language = user_language(context)
	await update.message.reply_text(
		UNKNOWN_TEXT_REPLIES.get(language, UNKNOWN_TEXT_REPLIES["ru"]),
		reply_markup=return_user_keyboard(context),
	)


async def _reply_no_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Кнопка раздела, по которому пока нет информации: название раздела и «Данных нет»."""
	language = user_language(context)
	await update.message.reply_text(no_data_card(language, update.message.text), parse_mode=HTML)


async def _show_section(update: Update, context: ContextTypes.DEFAULT_TYPE, section: str) -> None:
	"""Переключает меню колонии на раздел «Информация», «Услуги» или на главный экран."""
	context.user_data["menu_section"] = section
	text, keyboard = menu_screen(context, section)
	await update.message.reply_text(text, parse_mode=HTML, reply_markup=keyboard)


async def _send_hotel_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Карточка гостиницы рядом с колонией; чего нет — помечено «данных нет»."""
	message = update.message
	language = user_language(context)
	card = HOTEL_CARD_TEXTS.get(language, HOTEL_CARD_TEXTS["ru"])
	coordinates, phone = HOTEL_INFO.get(context.user_data["colony"], ((), ""))
	phone = phone.strip()
	if not coordinates and not phone:
		await message.reply_text(no_data_card(language, card["title"]), parse_mode=HTML)
		return

	missing = NO_DATA_TEXTS.get(language, NO_DATA_TEXTS["ru"]).lower()
	lines = [
		bold(card["title"]),
		"",
		f"{escape(card['location'])}: {escape(card['location_below'] if coordinates else missing)}",
		f"{escape(card['phone'])}: {escape(phone or missing)}",
	]
	await message.reply_text("\n".join(lines), parse_mode=HTML)
	if coordinates:
		await message.reply_location(latitude=coordinates[0], longitude=coordinates[1])


async def _send_additional_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Правила посещения, список разрешённого, номера колоний и памятки картинками."""
	message = update.message
	language = user_language(context)

	intro_image_path = ADDITIONAL_INFO_INTRO_IMAGE_PATHS.get(
		language,
		ADDITIONAL_INFO_INTRO_IMAGE_PATHS["ru"],
	)
	try:
		await send_cached_media(context.bot, message.chat_id, intro_image_path, is_photo=True)
	except OSError:
		await message.reply_text(no_data_text(language))

	await message.reply_text(ADDITIONAL_INFO_LIST_TEXTS.get(language, ADDITIONAL_INFO_LIST_TEXTS["ru"]))
	await message.reply_text(
		ADDITIONAL_INFO_COLONY_NUMBERS_TEXTS.get(language, ADDITIONAL_INFO_COLONY_NUMBERS_TEXTS["ru"])
	)

	image_paths = [
		*COLONY_REGIME_IMAGE_PATHS.get(language, COLONY_REGIME_IMAGE_PATHS["ru"]),
		*ADDITIONAL_INFO_IMAGE_PATHS,
	]
	existing_paths = [path for path in image_paths if os.path.exists(path)]
	try:
		if len(existing_paths) > 1:
			await send_cached_photo_album(context.bot, message.chat_id, existing_paths)
		elif existing_paths:
			await send_cached_media(context.bot, message.chat_id, existing_paths[0], is_photo=True)
		else:
			await message.reply_text(no_data_text(language))
	except OSError:
		await message.reply_text(no_data_text(language))


async def _send_colony_group_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Ссылка на родительскую группу выбранной колонии."""
	message = update.message
	language = user_language(context)
	group_keyboard = colony_group_link_keyboard(language, context.user_data["colony"])
	if not group_keyboard:
		title = COLONY_GROUP_BUTTONS.get(language, COLONY_GROUP_BUTTONS["ru"])
		await message.reply_text(no_data_card(language, title), parse_mode=HTML)
		return

	await message.reply_text(
		COLONY_GROUP_LINK_PROMPTS.get(language, COLONY_GROUP_LINK_PROMPTS["ru"]),
		reply_markup=group_keyboard,
	)
	colony_number = re.search(r"\d+", selected_colony_name(context, language))
	if colony_number:
		await message.reply_text(
			GROUP_SELECTED_TEXTS.get(language, GROUP_SELECTED_TEXTS["ru"]).format(
				number=colony_number.group()
			)
		)


async def _send_main_group_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	language = user_language(context)
	await update.message.reply_text(
		MAIN_GROUP_LINK_PROMPTS.get(language, MAIN_GROUP_LINK_PROMPTS["ru"]),
		reply_markup=main_group_link_keyboard(language),
	)


async def _send_colony_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	message = update.message
	language = user_language(context)
	coordinates = COLONY_COORDINATES.get(context.user_data["colony"])
	if not coordinates:
		title = colony_action_button_texts(language)[0]
		await message.reply_text(no_data_card(language, title), parse_mode=HTML)
		return

	colony_name = selected_colony_name(context, language).removeprefix("📍").strip()
	await message.reply_text(colony_location_prompt(language, colony_name))
	await message.reply_location(latitude=coordinates[0], longitude=coordinates[1])


async def _send_colony_directory(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	language = user_language(context)
	await update.message.reply_text(colony_directory_text(language, context.user_data["colony"]))


async def _ask_application_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	language = user_language(context)
	await update.message.reply_text(
		APPLICATION_TYPE_PROMPTS.get(language, APPLICATION_TYPE_PROMPTS["ru"]),
		reply_markup=application_type_keyboard(language),
	)


def _build_menu_actions() -> dict[str, tuple[MenuAction, bool]]:
	"""Подпись кнопки (на любом языке) → (действие, нужна ли выбранная колония)."""
	actions: dict[str, tuple[MenuAction, bool]] = {}

	def bind(labels: Iterable[str], action: MenuAction, needs_colony: bool) -> None:
		for label in labels:
			label = label.strip()
			if actions.get(label, (action, needs_colony)) != (action, needs_colony):
				raise ValueError(f"Button label {label!r} is bound to two different actions")
			actions[label] = (action, needs_colony)

	show_info = partial(_show_section, section="info")
	show_services = partial(_show_section, section="services")
	show_root = partial(_show_section, section="root")

	for language in SUPPORTED_LANGUAGES:
		# Последняя кнопка (my.gov) открывает WebApp и не присылает текст.
		hotel, shop, taxi, lawyers, money_transfer, additional_info, _ = ADDITIONAL_INFO_BUTTONS[language]
		info_section, services_section, back = MENU_SECTION_BUTTONS[language]
		location, directory, application = colony_action_button_texts(language)

		bind([info_section], show_info, needs_colony=True)
		bind([services_section], show_services, needs_colony=True)
		bind([back], show_root, needs_colony=True)
		bind([hotel], _send_hotel_info, needs_colony=True)
		bind([COLONY_GROUP_BUTTONS[language]], _send_colony_group_link, needs_colony=True)
		bind([location, COLONY_LOCATION_BUTTONS[language]], _send_colony_location, needs_colony=True)
		bind([directory, COLONY_DIRECTORY_BUTTONS[language]], _send_colony_directory, needs_colony=True)

		bind([application, COLONY_APPLICATION_BUTTONS[language]], _ask_application_type, needs_colony=False)
		bind([shop, taxi], _reply_no_data, needs_colony=False)
		bind([lawyers], handle_lawyer_button, needs_colony=False)
		bind([money_transfer], handle_money_transfer_button, needs_colony=False)
		bind([additional_info], _send_additional_info, needs_colony=False)
		bind([CLOTHING_BUTTONS[language]], handle_clothing_button, needs_colony=False)
		bind([CHANGE_COLONY_BUTTONS[language]], _ask_colony, needs_colony=False)
		bind([MAIN_GROUP_BUTTONS[language]], _send_main_group_link, needs_colony=False)
	return actions


MENU_ACTIONS = _build_menu_actions()


async def handle_menu_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Любой текст в личном чате, не обработанный раньше: кнопки меню и всё остальное."""
	message = update.message
	if not message or not message.text:
		return

	if await handle_lawyer_review_text(update, context):
		return

	action = MENU_ACTIONS.get(message.text.strip())
	if action is None:
		await _reply_unknown_text(update, context)
		return

	callback, needs_colony = action
	if needs_colony and context.user_data.get("colony") not in COLONY_GROUPS:
		await _resume_onboarding(update, context)
		return
	await callback(update, context)


async def handle_application_selection(
	update: Update,
	context: ContextTypes.DEFAULT_TYPE,
) -> None:
	"""Отправляет изображение образца заявления, выбранное пользователем."""
	query = update.callback_query
	if not query or not query.data:
		return

	language = user_language(context)
	image_type = query.data.removeprefix("application:")
	if image_type not in APPLICATION_IMAGE_PATHS:
		await query.answer(UNKNOWN_ACTION_TEXTS.get(language, UNKNOWN_ACTION_TEXTS["ru"]), show_alert=True)
		return

	await query.answer()
	chat = update.effective_chat
	if not chat:
		return

	image_path = APPLICATION_IMAGE_PATHS[image_type].get(
		language,
		APPLICATION_IMAGE_PATHS[image_type]["ru"],
	)
	try:
		await send_cached_media(context.bot, chat.id, image_path, is_photo=True)
	except OSError:
		await context.bot.send_message(chat_id=chat.id, text=no_data_text(language))

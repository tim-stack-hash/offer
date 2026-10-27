"""Обработка кнопок главного reply-меню выбранной колонии (локация, справочник, заявления и т.д.)."""

from __future__ import annotations

import os
import re
from contextlib import ExitStack

from telegram import InputMediaPhoto, Update
from telegram.ext import ContextTypes

from bot.config import (
	ADDITIONAL_INFO_IMAGE_PATHS,
	ADDITIONAL_INFO_INTRO_IMAGE_PATHS,
	APPLICATION_IMAGE_PATHS,
	COLONY_REGIME_IMAGE_PATHS,
)
from bot.content.colonies import COLONY_COORDINATES, HOTEL_INFO, colony_directory_text
from bot.functions.lawyer import handle_lawyer_review_text
from bot.content.texts import (
	ADDITIONAL_INFO_BUTTONS,
	ADDITIONAL_INFO_COLONY_NUMBERS_TEXTS,
	ADDITIONAL_INFO_IMAGE_MISSING_TEXTS,
	ADDITIONAL_INFO_LIST_TEXTS,
	ACTION_PROMPTS,
	APPLICATION_IMAGE_MISSING_TEXTS,
	APPLICATION_TYPE_PROMPTS,
	CHANGE_COLONY_BUTTONS,
	COLONY_APPLICATION_BUTTONS,
	COLONY_DIRECTORY_BUTTONS,
	COLONY_GROUP_BUTTONS,
	COLONY_GROUP_LINK_PROMPTS,
	COLONY_GROUP_MISSING_TEXTS,
	COLONY_LOCATION_BUTTONS,
	COLONY_PROMPTS,
	HOTEL_INFO_LABELS,
	HOTEL_INFO_MISSING_TEXTS,
	IN_DEVELOPMENT_TEXTS,
	LOCATION_MISSING_TEXTS,
	MAIN_GROUP_BUTTONS,
	MAIN_GROUP_LINK_PROMPTS,
	colony_action_button_texts,
	colony_location_prompt,
)
from bot.keyboards import (
	MENU_SECTION_BUTTONS,
	application_type_keyboard,
	colony_group_keyboard,
	colony_group_link_keyboard,
	colony_location_reply_keyboard,
	main_group_link_keyboard,
)


async def handle_location_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Разбирает нажатие любой кнопки главного меню колонии и отвечает нужным контентом."""
	message = update.message
	if not message or not message.text:
		return

	if await handle_lawyer_review_text(update, context):
		return

	button_text = message.text.strip()
	language = context.user_data.get("language", "ru")
	section_buttons = MENU_SECTION_BUTTONS.get(language, MENU_SECTION_BUTTONS["ru"])
	section_by_button = {section_buttons[0]: "info", section_buttons[1]: "services"}
	if button_text in section_by_button:
		context.user_data["menu_section"] = section_by_button[button_text]
		keyboard = colony_location_reply_keyboard(
			language,
			context.user_data.get("colony"),
			context.user_data["menu_section"],
		)
		if keyboard:
			await message.reply_text(
				ACTION_PROMPTS.get(language, ACTION_PROMPTS["ru"]),
				reply_markup=keyboard,
			)
		return
	if button_text == section_buttons[2]:
		context.user_data["menu_section"] = "root"
		keyboard = colony_location_reply_keyboard(
			language, context.user_data.get("colony"), "root"
		)
		if keyboard:
			await message.reply_text(
				ACTION_PROMPTS.get(language, ACTION_PROMPTS["ru"]),
				reply_markup=keyboard,
			)
		return
	additional_info_buttons = ADDITIONAL_INFO_BUTTONS.get(
		language,
		ADDITIONAL_INFO_BUTTONS["ru"],
	)
	if button_text == additional_info_buttons[0]:
		# Кнопка «Гостиница»: присылаем координаты и телефон, если они заданы для колонии.
		colony_group = context.user_data.get("colony")
		hotel_info = HOTEL_INFO.get(colony_group)
		if hotel_info is None:
			await message.reply_text(
				HOTEL_INFO_MISSING_TEXTS.get(
					language,
					HOTEL_INFO_MISSING_TEXTS["ru"],
				)
			)
			return

		coordinates, phone = hotel_info
		if not coordinates and not phone:
			await message.reply_text(
				HOTEL_INFO_MISSING_TEXTS.get(
					language,
					HOTEL_INFO_MISSING_TEXTS["ru"],
				)
			)
			return

		location_label, phone_label = HOTEL_INFO_LABELS.get(
			language,
			HOTEL_INFO_LABELS["ru"],
		)
		# Координаты и телефон заполнены не для всех колоний — отправляем то, что есть.
		reply_lines = []
		if coordinates:
			await message.reply_location(
				latitude=coordinates[0],
				longitude=coordinates[1],
			)
			reply_lines.append(location_label)
		if phone:
			reply_lines.append(f"{phone_label} {phone}")
		if reply_lines:
			await message.reply_text("\n".join(reply_lines))
		return
	if button_text == additional_info_buttons[5]:
		try:
			intro_image_path = ADDITIONAL_INFO_INTRO_IMAGE_PATHS.get(
				language,
				ADDITIONAL_INFO_INTRO_IMAGE_PATHS["ru"],
			)
			if os.path.exists(intro_image_path):
				with open(intro_image_path, "rb") as intro_image:
					await message.reply_photo(photo=intro_image)
			else:
				await message.reply_text(
					ADDITIONAL_INFO_IMAGE_MISSING_TEXTS.get(
						language,
						ADDITIONAL_INFO_IMAGE_MISSING_TEXTS["ru"],
					)
				)
		except OSError:
			await message.reply_text(
				ADDITIONAL_INFO_IMAGE_MISSING_TEXTS.get(
					language,
					ADDITIONAL_INFO_IMAGE_MISSING_TEXTS["ru"],
				)
			)
		await message.reply_text(
			ADDITIONAL_INFO_LIST_TEXTS.get(
				language,
				ADDITIONAL_INFO_LIST_TEXTS["ru"],
			)
		)
		await message.reply_text(
			ADDITIONAL_INFO_COLONY_NUMBERS_TEXTS.get(
				language,
				ADDITIONAL_INFO_COLONY_NUMBERS_TEXTS["ru"],
			)
		)
		try:
			image_paths = [
				*COLONY_REGIME_IMAGE_PATHS.get(
					language,
					COLONY_REGIME_IMAGE_PATHS["ru"],
				),
				*ADDITIONAL_INFO_IMAGE_PATHS,
			]
			existing_paths = [path for path in image_paths if os.path.exists(path)]
			if not existing_paths:
				await message.reply_text(
					ADDITIONAL_INFO_IMAGE_MISSING_TEXTS.get(
						language,
						ADDITIONAL_INFO_IMAGE_MISSING_TEXTS["ru"],
					)
				)
				return
			with ExitStack() as image_stack:
				media = [
					InputMediaPhoto(media=image_stack.enter_context(open(image_path, "rb")))
					for image_path in existing_paths
				]
				await message.reply_media_group(media=media)
		except OSError:
			await message.reply_text(
				ADDITIONAL_INFO_IMAGE_MISSING_TEXTS.get(
					language,
					ADDITIONAL_INFO_IMAGE_MISSING_TEXTS["ru"],
				)
			)
		return
	if button_text in additional_info_buttons[1:]:
		# Остальные дополнительные кнопки пока не реализованы.
		await message.reply_text(
			IN_DEVELOPMENT_TEXTS.get(language, IN_DEVELOPMENT_TEXTS["ru"])
		)
		return

	change_colony_text = CHANGE_COLONY_BUTTONS.get(
		language,
		CHANGE_COLONY_BUTTONS["ru"],
	)
	if button_text == change_colony_text:
		await message.reply_text(
			COLONY_PROMPTS.get(language, COLONY_PROMPTS["ru"]),
			reply_markup=colony_group_keyboard(language),
		)
		return

	group_button_texts = {text.strip() for text in COLONY_GROUP_BUTTONS.values()}
	if button_text in group_button_texts:
		colony_group = context.user_data.get("colony")
		group_keyboard = colony_group_link_keyboard(language, colony_group)
		if not group_keyboard:
			await message.reply_text(
				COLONY_GROUP_MISSING_TEXTS.get(
					language,
					COLONY_GROUP_MISSING_TEXTS["ru"],
				)
			)
			return

		await message.reply_text(
			COLONY_GROUP_LINK_PROMPTS.get(
				language,
				COLONY_GROUP_LINK_PROMPTS["ru"],
			),
			reply_markup=group_keyboard,
		)
		colony_name = context.user_data.get("colony_name") or colony_group
		colony_number = re.search(r"\d+", colony_name)
		if colony_number:
			number = colony_number.group()
			group_selected_texts = {
				"ru": f"✅ Группa {number}-й колонии.",
				"uz": f"✅ {number}-son koloniya guruhi.",
				"uz_cyr": f"✅ {number}-сон колония гуруҳи.",
			}
			await message.reply_text(group_selected_texts.get(language, group_selected_texts["ru"]))
		return

	main_group_button_text = MAIN_GROUP_BUTTONS.get(
		language,
		MAIN_GROUP_BUTTONS["ru"],
	)
	if button_text == main_group_button_text:
		await message.reply_text(
			MAIN_GROUP_LINK_PROMPTS.get(
				language,
				MAIN_GROUP_LINK_PROMPTS["ru"],
			),
			reply_markup=main_group_link_keyboard(language),
		)
		return

	# Кнопки «локация/справочник/заявления» зависят от номера колонии, поэтому
	# сверяем как актуальный текст с номером, так и старый текст без номера.
	location_text, directory_text, application_text = colony_action_button_texts(
		language,
		context.user_data.get("colony_name", ""),
	)
	legacy_application_text = COLONY_APPLICATION_BUTTONS.get(
		language,
		COLONY_APPLICATION_BUTTONS["ru"],
	)
	legacy_directory_text = COLONY_DIRECTORY_BUTTONS.get(
		language,
		COLONY_DIRECTORY_BUTTONS["ru"],
	)
	if button_text in (application_text, legacy_application_text):
		await message.reply_text(
			APPLICATION_TYPE_PROMPTS.get(language, APPLICATION_TYPE_PROMPTS["ru"]),
			reply_markup=application_type_keyboard(language),
		)
		return
	if button_text in (directory_text, legacy_directory_text):
		colony_group = context.user_data.get("colony")
		await message.reply_text(colony_directory_text(language, colony_group))
		return
	location_button_texts = {
		button_text
		for button_text in COLONY_LOCATION_BUTTONS.values()
	}
	location_button_texts.update(
		colony_action_button_texts(
			button_language,
			context.user_data.get("colony_name", ""),
		)[0]
		for button_language in COLONY_LOCATION_BUTTONS
	)
	if button_text not in location_button_texts:
		return

	colony_group = context.user_data.get("colony")
	coordinates = COLONY_COORDINATES.get(colony_group)
	if not coordinates:
		await message.reply_text(LOCATION_MISSING_TEXTS.get(language, LOCATION_MISSING_TEXTS["ru"]))
		return

	colony_name = (context.user_data.get("colony_name") or colony_group).removeprefix("📍").strip()
	await message.reply_text(colony_location_prompt(language, colony_name))
	await message.reply_location(latitude=coordinates[0], longitude=coordinates[1])


async def handle_application_selection(
	update: Update,
	context: ContextTypes.DEFAULT_TYPE,
) -> None:
	"""Отправляет изображение образца заявления, выбранное пользователем."""
	query = update.callback_query
	if not query or not query.data:
		return

	image_type = query.data.removeprefix("application:")
	if image_type not in APPLICATION_IMAGE_PATHS:
		await query.answer("Неизвестный тип заявления.", show_alert=True)
		return

	await query.answer()
	message = query.message
	if not message:
		return

	language = context.user_data.get("language", "ru")
	image_path = APPLICATION_IMAGE_PATHS[image_type].get(
		language,
		APPLICATION_IMAGE_PATHS[image_type]["ru"],
	)
	try:
		with open(image_path, "rb") as image_file:
			await message.reply_photo(photo=image_file)
	except OSError:
		await message.reply_text(
			APPLICATION_IMAGE_MISSING_TEXTS.get(
				language,
				APPLICATION_IMAGE_MISSING_TEXTS["ru"],
			)
		)

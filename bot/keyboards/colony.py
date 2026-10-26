"""Клавиатуры выбора колонии и главного меню выбранной колонии."""

from __future__ import annotations

from telegram import (
	InlineKeyboardButton,
	InlineKeyboardMarkup,
	KeyboardButton,
	ReplyKeyboardMarkup,
	WebAppInfo,
)

from bot.config import MY_GOV_URL
from bot.content.colonies import (
	COLONY_COORDINATES,
	COLONY_GROUP_LABELS,
	COLONY_GROUP_LINKS,
	COLONY_GROUPS,
)
from bot.content.texts import (
	ADDITIONAL_INFO_BUTTONS,
	APPLICATION_TYPE_BUTTONS,
	CHANGE_COLONY_BUTTONS,
	CHANGE_LANGUAGE_BUTTONS,
	CLOTHING_BUTTONS,
	COLONY_GROUP_BUTTONS,
	FEEDBACK_BUTTON_TEXT,
	MAIN_GROUP_BUTTONS,
	SUPPORT_BUTTON_TEXT,
	colony_action_button_texts,
)

 
def application_type_keyboard(language: str) -> InlineKeyboardMarkup:
	"""Инлайн-кнопки выбора длительного или краткосрочного свидания."""
	button_texts = APPLICATION_TYPE_BUTTONS.get(
		language,
		APPLICATION_TYPE_BUTTONS["ru"],
	)
	return InlineKeyboardMarkup(
		[
			[InlineKeyboardButton(button_texts[0], callback_data="application:long")],
			[InlineKeyboardButton(button_texts[1], callback_data="application:short")],
		]
	)


def colony_group_link_keyboard(language: str, colony_group: str) -> InlineKeyboardMarkup | None:
	"""Инлайн-кнопка со ссылкой на Telegram-группу выбранной колонии (или None, если ссылки нет)."""
	group_link = COLONY_GROUP_LINKS.get(colony_group)
	if not group_link:
		return None

	button_text = COLONY_GROUP_BUTTONS.get(language, COLONY_GROUP_BUTTONS["ru"])
	group_url = f"https://t.me/{group_link.removeprefix('@')}"
	return InlineKeyboardMarkup(
		[[InlineKeyboardButton(button_text, url=group_url)]]
	)


def colony_group_keyboard(language: str) -> InlineKeyboardMarkup:
	"""Инлайн-клавиатура со списком всех колоний для выбора."""
	labels = COLONY_GROUP_LABELS.get(language, COLONY_GROUP_LABELS["ru"])
	buttons = [
		InlineKeyboardButton(label, callback_data=f"colonies:select:{index}")
		for index, label in enumerate(labels)
	]
	return InlineKeyboardMarkup(
		[
			buttons[row_start:row_start + 2]
			for row_start in range(0, len(buttons), 2)
		]
	)


def colony_location_keyboard(language: str, colony_group: str) -> InlineKeyboardMarkup | None:
	"""Инлайн-кнопка «Локация» для выбранной колонии (или None, если координат нет)."""
	if colony_group not in COLONY_COORDINATES:
		return None

	colony_index = COLONY_GROUPS.index(colony_group)
	colony_name = COLONY_GROUP_LABELS.get(language, COLONY_GROUP_LABELS["ru"])[colony_index]
	button_text = colony_action_button_texts(language, colony_name)[0]
	return InlineKeyboardMarkup(
		[[InlineKeyboardButton(button_text, callback_data="colonies:location")]]
	)


MENU_SECTION_BUTTONS = {
	"ru": ("ℹ️ Информация", "🧰 Услуги", "⬅️ Назад"),
	"uz": ("ℹ️ Ma'lumot", "🧰 Xizmatlar", "⬅️ Orqaga"),
	"uz_cyr": ("ℹ️ Маълумот", "🧰 Хизматлар", "⬅️ Орқага"),
}


def colony_location_reply_keyboard(
	language: str,
	colony_group: str,
	section: str = "root",
) -> ReplyKeyboardMarkup | None:
	"""Главная reply-клавиатура меню колонии: локация, справочник, заявления, доп. кнопки."""
	if colony_group not in COLONY_GROUPS:
		return None

	colony_index = COLONY_GROUPS.index(colony_group)
	colony_name = COLONY_GROUP_LABELS.get(language, COLONY_GROUP_LABELS["ru"])[colony_index]
	location_text, directory_text, application_text = colony_action_button_texts(
		language,
		colony_name,
	)
	clothing_text = CLOTHING_BUTTONS.get(language, CLOTHING_BUTTONS["ru"])
	group_button_text = COLONY_GROUP_BUTTONS.get(
		language,
		COLONY_GROUP_BUTTONS["ru"],
	)
	main_group_button_text = MAIN_GROUP_BUTTONS.get(
		language,
		MAIN_GROUP_BUTTONS["ru"],
	)
	additional_info_buttons = ADDITIONAL_INFO_BUTTONS.get(
		language,
		ADDITIONAL_INFO_BUTTONS["ru"],
	)
	section_buttons = MENU_SECTION_BUTTONS.get(language, MENU_SECTION_BUTTONS["ru"])
	if section == "info":
		menu_rows = [
			[KeyboardButton(location_text), KeyboardButton(directory_text)],
			[KeyboardButton(application_text), KeyboardButton(additional_info_buttons[0])],
			[KeyboardButton(additional_info_buttons[1]), KeyboardButton(additional_info_buttons[5])],
			[
				KeyboardButton(additional_info_buttons[6], web_app=WebAppInfo(url=MY_GOV_URL)),
				KeyboardButton(section_buttons[2]),
			],
		]
	elif section == "services":
		menu_rows = [
			[KeyboardButton(clothing_text), KeyboardButton(additional_info_buttons[2])],
			[KeyboardButton(additional_info_buttons[3]), KeyboardButton(additional_info_buttons[4])],
			[
				KeyboardButton(additional_info_buttons[6], web_app=WebAppInfo(url=MY_GOV_URL)),
				KeyboardButton(section_buttons[2]),
			],
		]
	else:
		menu_rows = [[KeyboardButton(section_buttons[0]), KeyboardButton(section_buttons[1])]]
	if section == "root":
		menu_rows.extend([
			[KeyboardButton(group_button_text), KeyboardButton(main_group_button_text)],
			[
				KeyboardButton(CHANGE_COLONY_BUTTONS.get(language, CHANGE_COLONY_BUTTONS["ru"])),
				KeyboardButton(CHANGE_LANGUAGE_BUTTONS.get(language, CHANGE_LANGUAGE_BUTTONS["ru"])),
			],
			[
				KeyboardButton(FEEDBACK_BUTTON_TEXT.get(language, FEEDBACK_BUTTON_TEXT["ru"])),
				KeyboardButton(SUPPORT_BUTTON_TEXT.get(language, SUPPORT_BUTTON_TEXT["ru"])),
			],
		])
	return ReplyKeyboardMarkup(
		menu_rows,
		resize_keyboard=True,
		is_persistent=True,
	)

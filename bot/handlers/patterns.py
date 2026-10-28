"""Регулярные выражения для распознавания локализованных reply-кнопок."""

from __future__ import annotations

import re
from collections.abc import Iterable

from bot.config import SUPPORTED_LANGUAGES
from bot.content.clothing_regions import CLOTHING_REGIONS
from bot.content.colonies import COLONY_GROUP_LABELS
from bot.content.lawyer_regions import LAWYER_REGIONS
from bot.content.texts import (
	ADDITIONAL_INFO_BUTTONS,
	CHANGE_COLONY_BUTTONS,
	CHANGE_LANGUAGE_BUTTONS,
	CLOTHING_BUTTONS,
	COLONY_APPLICATION_BUTTONS,
	COLONY_DIRECTORY_BUTTONS,
	COLONY_GROUP_BUTTONS,
	COLONY_LOCATION_BUTTONS,
	FEEDBACK_BUTTON_TEXT,
	FEEDBACK_CATEGORY_BUTTONS,
	LANGUAGE_BUTTONS,
	MAIN_GROUP_BUTTONS,
	SUPPORT_BUTTON_TEXT,
	SUPPORT_CANCEL_BUTTONS,
	colony_action_button_texts,
)
from bot.keyboards import MENU_SECTION_BUTTONS

# Подписи языковых кнопок из прошлых версий бота — у пользователей могут остаться старые клавиатуры.
LEGACY_LANGUAGE_LABELS = {"O'zbekcha": "uz", "Русский": "ru", "Узбекча": "uz_cyr"}


def exact_text_pattern(texts: Iterable[str]) -> str:
	"""Regexp, совпадающий ровно с одним из текстов (с допуском пробелов по краям)."""
	alternatives = sorted({text.strip() for text in texts if text.strip()}, key=len, reverse=True)
	return r"^\s*(?:" + "|".join(re.escape(text) for text in alternatives) + r")\s*$"


def language_by_label(text: str) -> str | None:
	"""Определяет код языка по подписи кнопки."""
	text = text.strip()
	return dict(LANGUAGE_BUTTONS).get(text) or LEGACY_LANGUAGE_LABELS.get(text)


LANGUAGE_LABELS = frozenset(
	[label for label, _ in LANGUAGE_BUTTONS] + list(LEGACY_LANGUAGE_LABELS)
)

LANGUAGE_PATTERN = exact_text_pattern(LANGUAGE_LABELS)
CHANGE_LANGUAGE_PATTERN = exact_text_pattern(CHANGE_LANGUAGE_BUTTONS.values())
SUPPORT_BUTTON_PATTERN = exact_text_pattern(SUPPORT_BUTTON_TEXT.values())
CANCEL_PATTERN = exact_text_pattern(SUPPORT_CANCEL_BUTTONS.values())
FEEDBACK_BUTTON_PATTERN = exact_text_pattern(FEEDBACK_BUTTON_TEXT.values())
FEEDBACK_CATEGORY_PATTERN = exact_text_pattern(
	text for buttons in FEEDBACK_CATEGORY_BUTTONS.values() for text in buttons
)


def _all_button_labels() -> frozenset[str]:
	"""Подписи всех reply-кнопок бота на всех языках, а также команды меню."""
	labels = {"/start", "/menu", "/help", *LANGUAGE_LABELS}
	for language in SUPPORTED_LANGUAGES:
		for mapping in (
			CHANGE_COLONY_BUTTONS,
			CHANGE_LANGUAGE_BUTTONS,
			CLOTHING_BUTTONS,
			COLONY_APPLICATION_BUTTONS,
			COLONY_DIRECTORY_BUTTONS,
			COLONY_GROUP_BUTTONS,
			COLONY_LOCATION_BUTTONS,
			MAIN_GROUP_BUTTONS,
			FEEDBACK_BUTTON_TEXT,
			SUPPORT_BUTTON_TEXT,
			SUPPORT_CANCEL_BUTTONS,
		):
			labels.add(mapping[language])
		labels.update(ADDITIONAL_INFO_BUTTONS[language])
		labels.update(FEEDBACK_CATEGORY_BUTTONS[language])
		labels.update(MENU_SECTION_BUTTONS[language])
		labels.update(COLONY_GROUP_LABELS[language])
		labels.update(colony_action_button_texts(language))
		labels.update(region.get(language, region["ru"]) for region in CLOTHING_REGIONS.values())
		labels.update(region.get(language, region["ru"]) for region in LAWYER_REGIONS.values())
	return frozenset(label.strip() for label in labels)


# Используется, чтобы отличать нажатия кнопок от свободного текста пользователя.
BUTTON_LABELS = _all_button_labels()

from __future__ import annotations

import re

from bot.content.texts import ADDITIONAL_INFO_BUTTONS, SUPPORT_BUTTON_TEXT
from bot.handlers.patterns import (
	BUTTON_LABELS,
	LANGUAGE_PATTERN,
	SUPPORT_BUTTON_PATTERN,
	exact_text_pattern,
	language_by_label,
)


def test_exact_pattern_escapes_and_matches_whole_text():
	pattern = exact_text_pattern(["a+b", "c"])
	assert re.match(pattern, "a+b")
	assert re.match(pattern, " c ")
	assert not re.match(pattern, "a+bc")


def test_language_labels_including_legacy_ones():
	assert language_by_label("Русский") == "ru"
	assert language_by_label("Узбекча") == "uz_cyr"
	assert language_by_label("hello") is None
	assert re.match(LANGUAGE_PATTERN, "O'zbekcha")


def test_support_button_matches_every_language():
	for text in SUPPORT_BUTTON_TEXT.values():
		assert re.match(SUPPORT_BUTTON_PATTERN, text)


def test_menu_buttons_are_known_labels():
	for buttons in ADDITIONAL_INFO_BUTTONS.values():
		assert set(buttons) <= BUTTON_LABELS
	assert "просто текст" not in BUTTON_LABELS

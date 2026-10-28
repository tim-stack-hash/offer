"""Каждый текст интерфейса должен быть на всех языках бота."""

from __future__ import annotations

import bot.content.texts as texts
from bot.config import SUPPORTED_LANGUAGES


def _localized_texts():
	for name in texts.__all__:
		value = getattr(texts, name)
		if isinstance(value, dict) and set(value) & set(SUPPORTED_LANGUAGES):
			yield name, value


def test_every_interface_text_is_translated():
	untranslated = {
		name: sorted(set(SUPPORTED_LANGUAGES) - set(value))
		for name, value in _localized_texts()
		if not set(SUPPORTED_LANGUAGES) <= set(value)
	}
	assert untranslated == {}


def test_translations_are_not_empty():
	empty = [
		(name, language)
		for name, value in _localized_texts()
		for language, text in value.items()
		if isinstance(text, str) and not text.strip()
	]
	assert empty == []


def test_colony_names_have_no_stray_symbols():
	from bot.content.colonies import COLONY_GROUP_LABELS

	broken = [
		label
		for labels in COLONY_GROUP_LABELS.values()
		for label in labels
		if label != label.strip() or label.count("(") != label.count(")")
	]
	assert broken == []

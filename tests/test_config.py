from __future__ import annotations

import pytest

from bot.config import (
	APPLICATION_IMAGE_PATHS,
	ADDITIONAL_INFO_IMAGE_PATHS,
	ADDITIONAL_INFO_INTRO_IMAGE_PATHS,
	COLONY_REGIME_IMAGE_PATHS,
	get_support_chat_id,
	parse_admin_user_ids,
)


def test_admin_ids_are_parsed(monkeypatch):
	monkeypatch.setenv("ADMIN_USER_IDS", "10, 20,")
	assert parse_admin_user_ids() == frozenset({10, 20})


@pytest.mark.parametrize("value", ["", "abc", "-5"])
def test_invalid_admin_ids_are_rejected(monkeypatch, value):
	monkeypatch.setenv("ADMIN_USER_IDS", value)
	with pytest.raises(RuntimeError):
		parse_admin_user_ids()


def test_empty_chat_id_falls_back_to_default(monkeypatch):
	monkeypatch.setenv("SUPPORT_CHAT_ID", "")
	assert get_support_chat_id() < 0


def test_all_bundled_images_exist():
	import os

	paths = [
		*(path for by_language in APPLICATION_IMAGE_PATHS.values() for path in by_language.values()),
		*(path for pair in COLONY_REGIME_IMAGE_PATHS.values() for path in pair),
		*ADDITIONAL_INFO_INTRO_IMAGE_PATHS.values(),
		*ADDITIONAL_INFO_IMAGE_PATHS,
	]
	missing = [path for path in paths if not os.path.exists(path)]
	assert not missing

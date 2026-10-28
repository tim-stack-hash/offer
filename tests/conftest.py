"""Общие фикстуры: изолированная база и минимальное окружение."""

from __future__ import annotations

import pytest

from bot.database import initialize_user_database
from bot.services import subscription


@pytest.fixture(autouse=True)
def environment(tmp_path, monkeypatch):
	monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123456:TEST")
	monkeypatch.setenv("ADMIN_USER_IDS", "1")
	monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "bot.sqlite3"))
	monkeypatch.setenv("PERSISTENCE_PATH", str(tmp_path / "state.pickle"))
	initialize_user_database()
	subscription._confirmed_members.clear()

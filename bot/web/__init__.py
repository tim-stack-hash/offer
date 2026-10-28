"""Веб-панель администратора (только чтение, HTTP Basic Auth)."""

from bot.web.app import create_app

__all__ = ["create_app"]

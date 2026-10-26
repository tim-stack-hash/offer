"""Публичный интерфейс пакета: обработчики, связанные с колониями."""

from __future__ import annotations

from bot.handlers.colony.menu import handle_application_selection, handle_location_button
from bot.handlers.colony.selection import handle_colony_selection

__all__ = [
	"handle_colony_selection",
	"handle_application_selection",
	"handle_location_button",
]

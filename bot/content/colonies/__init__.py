"""Публичный интерфейс пакета: справочные данные по колониям из тематических модулей."""

from __future__ import annotations

from bot.content.colonies.directory import (
	COLONY_DIRECTORY_CONTACTS,
	COLONY_DIRECTORY_HEADERS,
	colony_directory_text,
)
from bot.content.colonies.directory_data import COLONY_DIRECTORY_EXTRA_CONTACTS
from bot.content.colonies.groups import (
	COLONY_COORDINATES,
	COLONY_GROUP_LABELS,
	COLONY_GROUP_LINKS,
	COLONY_GROUPS,
	HOTEL_INFO,
)

__all__ = [
	"COLONY_COORDINATES",
	"COLONY_DIRECTORY_CONTACTS",
	"COLONY_DIRECTORY_EXTRA_CONTACTS",
	"COLONY_DIRECTORY_HEADERS",
	"COLONY_GROUP_LABELS",
	"COLONY_GROUP_LINKS",
	"COLONY_GROUPS",
	"HOTEL_INFO",
	"colony_directory_text",
]

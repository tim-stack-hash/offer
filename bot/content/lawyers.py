"""Карточки адвокатов, сгруппированные по регионам."""

from __future__ import annotations

import os

from bot.config import PROJECT_ROOT

LAWYERS = {
	"tima": {
		"region": "tashkent_city",
		"name": "Тима",
		"photo_path": os.path.join(PROJECT_ROOT, "Тима.jpg"),
		"phone_number": "+998938807766",
	},
}

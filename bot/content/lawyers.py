"""Карточки адвокатов, сгруппированные по регионам."""

from __future__ import annotations

import os

from bot.config import LAWYER_PHOTOS_DIR

LAWYERS = {
	"tima": {
		"region": "tashkent_city",
		"name": "Тима",
		"photo_path": os.path.join(LAWYER_PHOTOS_DIR, "tima.jpg"),
		"phone_number": "+998938807766",
	},
}

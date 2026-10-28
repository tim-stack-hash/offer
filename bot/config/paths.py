"""Пути к файлам проекта: медиа, база данных и состояние бота."""

from __future__ import annotations

import os

# Корень проекта — на два уровня выше пакета bot/config/.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
VIDEOS_DIR = os.path.join(ASSETS_DIR, "videos")

# Каталог с изменяемыми данными (SQLite, состояние диалогов) — не хранится в git.
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

DEFAULT_DATABASE_PATH = os.path.join(DATA_DIR, "bot_users.sqlite3")
DEFAULT_PERSISTENCE_PATH = os.path.join(DATA_DIR, "bot_state.pickle")

# Расположение базы до переезда в data/: переносится автоматически при первом запуске.
LEGACY_USER_DATABASE_PATH = os.path.join(PROJECT_ROOT, "bot_users.sqlite3")


def _image(*parts: str) -> str:
	return os.path.join(IMAGES_DIR, *parts)


# Образцы заявлений о свидании по сроку и языку.
APPLICATION_IMAGE_PATHS = {
	"long": {
		"ru": _image("applications", "long_ru.png"),
		"uz": _image("applications", "long_uz.png"),
		"uz_cyr": _image("applications", "long_uz.png"),
	},
	"short": {
		"ru": _image("applications", "short_ru.png"),
		"uz": _image("applications", "short_uz.png"),
		"uz_cyr": _image("applications", "short_uz.png"),
	},
}

# Изображения режимов содержания, отправляемые по кнопке «Доп. информация».
COLONY_REGIME_IMAGE_PATHS = {
	"ru": (_image("regimes", "general_ru.jpg"), _image("regimes", "strict_ru.jpg")),
	"uz": (_image("regimes", "general_uz.jpg"), _image("regimes", "strict_uz.jpg")),
	"uz_cyr": (_image("regimes", "general_uz_cyr.jpg"), _image("regimes", "strict_uz_cyr.jpg")),
}

ADDITIONAL_INFO_INTRO_IMAGE_PATHS = {
	"ru": _image("additional_info", "intro_ru.jpg"),
	"uz": _image("additional_info", "intro_uz.jpg"),
	"uz_cyr": _image("additional_info", "intro_uz.jpg"),
}

ADDITIONAL_INFO_IMAGE_PATHS = (
	_image("additional_info", "info_1.jpg"),
	_image("additional_info", "info_2.jpg"),
	_image("additional_info", "guin_numbers.jpg"),
)

# Медиа с инструкциями по переводу денег: (путь, это фото?). Отсутствующие файлы пропускаются.
MONEY_TRANSFER_MEDIA = (
	(_image("money_transfer", "smart.jpg"), True),
	(os.path.join(VIDEOS_DIR, "money_transfer", "paynet.mp4"), False),
	(os.path.join(VIDEOS_DIR, "money_transfer", "uzum.mp4"), False),
	(os.path.join(VIDEOS_DIR, "money_transfer", "paynet_kocha.mp4"), False),
)

LAWYER_PHOTOS_DIR = _image("lawyers")


def media_cache_key(path: str) -> str:
	"""Ключ кеша file_id, не зависящий от расположения проекта на диске."""
	return os.path.relpath(path, PROJECT_ROOT).replace(os.sep, "/")

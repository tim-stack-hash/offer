"""Настройки бота: переменные окружения, пути к файлам и список администраторов."""

from __future__ import annotations

import os

# Корень проекта (папка, где лежит main.py) — на один уровень выше пакета bot/.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ссылка на портал my.gov.uz, открываемый из клавиатуры Telegram WebApp.
MY_GOV_URL = "https://my.gov.uz/uz/service/611"

# Ссылки Google Play на мобильные приложения.
PAYNET_APP_URL = "https://play.google.com/store/apps/details?id=uz.paynet.app"
UZUM_BANK_APP_URL = "https://play.google.com/store/apps/details?id=uz.kapitalbank.android"

# Путь к файлу базы данных пользователей (хранится в корне проекта).
USER_DATABASE_PATH = os.path.join(PROJECT_ROOT, "bot_users.sqlite3")

# Пути к изображениям образцов заявлений о свидании по языку и сроку.
APPLICATION_IMAGE_PATHS = {
	"long": {
		"ru": os.path.join(PROJECT_ROOT, "imgs", "длит_встр.png"),
		"uz": os.path.join(PROJECT_ROOT, "imgs", "узок_муддат.png"),
		"uz_cyr": os.path.join(PROJECT_ROOT, "imgs", "узок_муддат.png"),
	},
	"short": {
		"ru": os.path.join(PROJECT_ROOT, "imgs", "кратк_встр.png"),
		"uz": os.path.join(PROJECT_ROOT, "imgs", "киска_муддат.png"),
		"uz_cyr": os.path.join(PROJECT_ROOT, "imgs", "киска_муддат.png"),
	},
}

# Изображения, отправляемые по кнопке «Доп. информация».
COLONY_REGIME_IMAGE_PATHS = {
	"ru": (
		os.path.join(PROJECT_ROOT, "imgs", "общий режим.jpg"),
		os.path.join(PROJECT_ROOT, "imgs", "строгий режим.jpg"),
	),
	"uz": (
		os.path.join(PROJECT_ROOT, "imgs", "umumiy tartib.jpg"),
		os.path.join(PROJECT_ROOT, "imgs", "qattiq tartib.jpg"),
	),
	"uz_cyr": (
		os.path.join(PROJECT_ROOT, "imgs", "умумий тартиб.jpg"),
		os.path.join(PROJECT_ROOT, "imgs", "каттик тартиб.jpg"),
	),
}

ADDITIONAL_INFO_INTRO_IMAGE_PATHS = {
	"ru": os.path.join(PROJECT_ROOT, "imgs", "btashrif_ru.jpg"),
	"uz": os.path.join(PROJECT_ROOT, "imgs", "exp.smart-rules.jpg"),
	"uz_cyr": os.path.join(PROJECT_ROOT, "imgs", "exp.smart-rules.jpg"),
}

ADDITIONAL_INFO_IMAGE_PATHS = (
	os.path.join(PROJECT_ROOT, "imgs", "Доп инфо.jpg"),
	os.path.join(PROJECT_ROOT, "imgs", "доп инфо2.jpg"),
	os.path.join(PROJECT_ROOT, "imgs", "номера гуина доп инфо.jpg"),
)

# Группа, в которую пользователь должен вступить для работы с ботом.
SUBSCRIPTION_CHAT_ID = "@smartdunyopaygroup"
SUBSCRIPTION_GROUP_URL = "https://t.me/smartdunyopaygroup"

# Медиа с инструкциями по переводу денег.
MONEY_TRANSFER_MEDIA_PATHS = (
	os.path.join(PROJECT_ROOT, "Smart Dunyo vds", "Smart.jpg"),
	os.path.join(PROJECT_ROOT, "Smart Dunyo vds", "Paynet & Smart.mp4"),
	os.path.join(PROJECT_ROOT, "Smart Dunyo vds", "Uzum & Smart.mp4"),
	os.path.join(PROJECT_ROOT, "Smart Dunyo vds", "Paynet Kocha & Smart.mp4"),
)

# Ссылка на группу с образцами одежды.
CLOTHING_LINK_URL = "https://t.me/kiyimlar_namuna"

# ID канала, куда бот публикует отзывы об адвокатах по умолчанию.
DEFAULT_LAWYER_REVIEWS_CHAT_ID = -1003735132281
LAWYER_REVIEWS_CHAT_ID_ENV = "LAWYER_REVIEWS_CHAT_ID"
SUPPORT_CHAT_ID_ENV = "SUPPORT_CHAT_ID"
DEFAULT_SUPPORT_CHAT_ID = -1003799306220
FEEDBACK_CHAT_ID_ENV = "FEEDBACK_CHAT_ID"
DEFAULT_FEEDBACK_CHAT_ID = -5089507473

# Имя переменной окружения со списком Telegram ID администраторов бота.
ADMIN_USER_IDS_ENV = "ADMIN_USER_IDS"

# Дополнительные пользователи, которым разрешены только ответы в поддержку.
SUPPORT_REPLY_USER_IDS = frozenset({5712520579, 1024084332, 1239647560})

# Префикс строки с количеством пользователей в коротком описании бота.
USER_COUNT_DESCRIPTION_PREFIX = "👥 Пользователей: "

# Максимальная длина короткого описания бота в Telegram.
BOT_SHORT_DESCRIPTION_LIMIT = 120


def parse_admin_user_ids() -> frozenset[int]:
	"""Читает и проверяет список Telegram ID администраторов из переменной окружения."""
	raw_admin_ids = os.getenv(ADMIN_USER_IDS_ENV, "").strip()
	if not raw_admin_ids:
		raise RuntimeError(
			f"Set {ADMIN_USER_IDS_ENV} to the Telegram ID of at least one bot administrator"
		)

	try:
		admin_ids = [int(value.strip()) for value in raw_admin_ids.split(",")]
	except ValueError as error:
		raise RuntimeError(
			f"{ADMIN_USER_IDS_ENV} must contain comma-separated numeric Telegram IDs"
		) from error

	if any(admin_id <= 0 for admin_id in admin_ids):
		raise RuntimeError(f"{ADMIN_USER_IDS_ENV} must contain positive Telegram IDs")
	return frozenset(admin_ids)


def is_admin(user_id: int) -> bool:
	"""Проверяет, входит ли указанный Telegram ID в список администраторов."""
	return user_id in parse_admin_user_ids()


def get_lawyer_reviews_chat_id() -> int:
	"""Читает ID канала отзывов из окружения или использует настроенный ID по умолчанию."""
	raw_chat_id = os.getenv(
		LAWYER_REVIEWS_CHAT_ID_ENV,
		str(DEFAULT_LAWYER_REVIEWS_CHAT_ID),
	).strip()
	try:
		return int(raw_chat_id)
	except ValueError as error:
		raise RuntimeError(
			f"{LAWYER_REVIEWS_CHAT_ID_ENV} must be a numeric Telegram chat ID"
		) from error


def get_support_chat_id() -> int:
	"""Читает ID канала поддержки из окружения или использует ID по умолчанию."""
	raw_chat_id = os.getenv(
		SUPPORT_CHAT_ID_ENV,
		str(DEFAULT_SUPPORT_CHAT_ID),
	).strip()
	try:
		return int(raw_chat_id)
	except ValueError as error:
		raise RuntimeError(
			f"{SUPPORT_CHAT_ID_ENV} must be a numeric Telegram chat ID"
		) from error


def get_feedback_chat_id() -> int:
	"""Читает ID группы предложений и жалоб из окружения или использует ID по умолчанию."""
	raw_chat_id = os.getenv(
		FEEDBACK_CHAT_ID_ENV,
		str(DEFAULT_FEEDBACK_CHAT_ID),
	).strip()
	try:
		return int(raw_chat_id)
	except ValueError as error:
		raise RuntimeError(
			f"{FEEDBACK_CHAT_ID_ENV} must be a numeric Telegram chat ID"
		) from error

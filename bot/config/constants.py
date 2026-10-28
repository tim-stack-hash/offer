"""Неизменяемые настройки бота: ссылки, ID чатов по умолчанию, лимиты."""

from __future__ import annotations

from datetime import timedelta, timezone

# Все даты в боте и выгрузках показываются по времени Ташкента.
LOCAL_TIMEZONE = timezone(timedelta(hours=5))

SUPPORTED_LANGUAGES = ("ru", "uz", "uz_cyr")
DEFAULT_LANGUAGE = "ru"

# Ссылка на портал my.gov.uz, открываемый из клавиатуры Telegram WebApp.
MY_GOV_URL = "https://my.gov.uz/uz/service/611"

# Ссылки Google Play на мобильные приложения.
PAYNET_APP_URL = "https://play.google.com/store/apps/details?id=uz.paynet.app"
UZUM_BANK_APP_URL = "https://play.google.com/store/apps/details?id=uz.kapitalbank.android"

# Группа, в которую пользователь должен вступить для работы с ботом.
SUBSCRIPTION_CHAT_ID = "@smartdunyopaygroup"
SUBSCRIPTION_GROUP_URL = "https://t.me/smartdunyopaygroup"

# Ссылка на группу с образцами одежды.
CLOTHING_LINK_URL = "https://t.me/kiyimlar_namuna"

# ID чатов по умолчанию; переопределяются переменными окружения.
DEFAULT_LAWYER_REVIEWS_CHAT_ID = -1003735132281
DEFAULT_SUPPORT_CHAT_ID = -1003799306220
DEFAULT_FEEDBACK_CHAT_ID = -5089507473

# Дополнительные пользователи, которым разрешены только ответы в поддержку.
SUPPORT_REPLY_USER_IDS = frozenset({5712520579, 1024084332, 1239647560})

# Префикс строки с количеством пользователей в коротком описании бота.
USER_COUNT_DESCRIPTION_PREFIX = "👥 Пользователей: "

# Максимальная длина короткого описания бота в Telegram.
BOT_SHORT_DESCRIPTION_LIMIT = 120

# Максимальная длина текстового сообщения пользователя в обращениях (символы UTF-16).
MAX_USER_MESSAGE_LENGTH = 3500

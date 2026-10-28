"""Сборка и запуск Telegram-приложения."""

from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from telegram import BotCommand, Update
from telegram.error import TelegramError
from telegram.ext import (
	Application,
	ContextTypes,
	Defaults,
	PersistenceInput,
	PicklePersistence,
)
from telegram.request import BaseRequest

from bot.config import (
	get_bot_token,
	get_log_level,
	get_persistence_path,
	is_content_protected,
	validate_settings,
)
from bot.content.texts import ERROR_TEXTS
from bot.database import initialize_user_database
from bot.handlers import register_handlers
from bot.handlers.common import user_language
from bot.jobs import schedule_jobs

LOGGER = logging.getLogger(__name__)

# Описания команд в меню Telegram: русские по умолчанию и узбекские для тех,
# у кого Telegram на узбекском (у Telegram нет отдельного кода для кириллицы).
BOT_COMMANDS: dict[str | None, list[BotCommand]] = {
	None: [
		BotCommand("start", "Запустить бота"),
		BotCommand("menu", "Выбрать язык и колонию"),
	],
	"uz": [
		BotCommand("start", "Botni ishga tushirish"),
		BotCommand("menu", "Til va koloniyani tanlash"),
	],
}


async def handle_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Логирует необработанные ошибки и сообщает пользователю, что что-то пошло не так."""
	LOGGER.error("Unhandled exception while processing update %s", update, exc_info=context.error)

	if not isinstance(update, Update):
		return
	chat = update.effective_chat
	if not chat or chat.type != "private":
		return
	try:
		language = user_language(context)
		await context.bot.send_message(chat.id, ERROR_TEXTS.get(language, ERROR_TEXTS["ru"]))
	except TelegramError:
		pass


async def _post_init(application: Application) -> None:
	"""Выполняется перед стартом polling: база, задачи по расписанию, команды меню."""
	initialize_user_database()
	schedule_jobs(application)
	for language_code, commands in BOT_COMMANDS.items():
		await application.bot.set_my_commands(commands, language_code=language_code)


def build_application(request: BaseRequest | None = None) -> Application:
	"""Создаёт приложение со всеми обработчиками и хранением состояния между перезапусками.

	request подменяет HTTP-клиент Bot API — так тесты прогоняют обновления без сети.
	"""
	persistence_path = get_persistence_path()
	os.makedirs(os.path.dirname(persistence_path) or ".", exist_ok=True)
	persistence = PicklePersistence(
		filepath=persistence_path,
		store_data=PersistenceInput(bot_data=False, chat_data=False, callback_data=False),
		update_interval=30,
	)

	builder = (
		Application.builder()
		.token(get_bot_token())
		.persistence(persistence)
		.post_init(_post_init)
	)
	if request is not None:
		builder = builder.request(request).get_updates_request(request)
	if is_content_protected():
		builder = builder.defaults(Defaults(protect_content=True))

	application = builder.build()
	register_handlers(application)
	application.add_error_handler(handle_error)
	return application


def configure_logging() -> None:
	logging.basicConfig(
		format="%(asctime)s %(levelname)s %(name)s: %(message)s",
		level=get_log_level(),
	)
	# httpx пишет в INFO каждый запрос getUpdates — это засоряет лог.
	logging.getLogger("httpx").setLevel(logging.WARNING)


def run() -> None:
	"""Точка входа: читает .env, проверяет настройки и запускает long polling."""
	load_dotenv()
	configure_logging()
	try:
		validate_settings()
	except RuntimeError as error:
		LOGGER.critical("Configuration error: %s. See .env.example", error)
		raise SystemExit(1) from None

	application = build_application()
	LOGGER.info("Starting bot (protect_content=%s)", is_content_protected())
	application.run_polling(allowed_updates=Update.ALL_TYPES)

"""Поддельный Bot API: настоящее приложение обрабатывает обновления без сети.

FakeBotApi подставляется вместо HTTP-клиента, записывает каждый вызов Bot API и
отвечает правдоподобными данными. ChatSimulator изображает пользователя в личном
чате: пишет текст, нажимает кнопки, делится контактом.
"""

from __future__ import annotations

import itertools
import json
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from telegram import Update
from telegram.ext import Application, ContextTypes
from telegram.request import BaseRequest, RequestData

from bot.app import build_application

BOT_USER = {"id": 999, "is_bot": True, "first_name": "Smart Dunyo", "username": "smart_dunyo_test_bot"}
MESSAGE_DATE = 1_760_000_000
SUBSCRIPTION_GROUP = {
	"id": -100500,
	"type": "supergroup",
	"title": "Smart Dunyo",
	"username": "smartdunyopaygroup",
}


@dataclass
class ApiCall:
	method: str
	params: dict[str, Any]
	result: Any


class FakeBotApi(BaseRequest):
	"""Записывает вызовы Bot API и отвечает так, как ответил бы Telegram."""

	def __init__(self) -> None:
		self.calls: list[ApiCall] = []
		self.member_status = "member"
		self._ids = itertools.count(1000)

	@property
	def read_timeout(self) -> float:
		return 5.0

	async def initialize(self) -> None:
		pass

	async def shutdown(self) -> None:
		pass

	async def do_request(
		self,
		url: str,
		method: str,
		request_data: RequestData | None = None,
		read_timeout: object = None,
		write_timeout: object = None,
		connect_timeout: object = None,
		pool_timeout: object = None,
	) -> tuple[int, bytes]:
		api_method = url.rsplit("/", 1)[-1]
		params = request_data.parameters if request_data else {}
		result = self._result(api_method, params)
		self.calls.append(ApiCall(api_method, params, result))
		return 200, json.dumps({"ok": True, "result": result}).encode()

	def _message(self, params: dict[str, Any], **content: Any) -> dict[str, Any]:
		chat_id = params.get("chat_id", 0)
		is_private = isinstance(chat_id, int) and chat_id > 0
		return {
			"message_id": next(self._ids),
			"date": MESSAGE_DATE,
			"chat": {"id": chat_id, "type": "private" if is_private else "supergroup"},
			"from": BOT_USER,
			"text": params.get("text", ""),
			**content,
		}

	def _photo(self) -> list[dict[str, Any]]:
		number = next(self._ids)
		return [{"file_id": f"photo-{number}", "file_unique_id": f"p{number}", "width": 1, "height": 1}]

	def _result(self, method: str, params: dict[str, Any]) -> Any:
		if method == "getMe":
			return BOT_USER
		if method == "getChatMember":
			user = {"id": params["user_id"], "is_bot": False, "first_name": "Test"}
			return {"status": self.member_status, "user": user}
		if method == "getMyShortDescription":
			return {"short_description": ""}
		if method == "copyMessage":
			return {"message_id": next(self._ids)}
		if method == "sendPhoto":
			return self._message(params, photo=self._photo())
		if method == "sendVideo":
			number = next(self._ids)
			video = {
				"file_id": f"video-{number}",
				"file_unique_id": f"v{number}",
				"width": 1,
				"height": 1,
				"duration": 1,
			}
			return self._message(params, video=video)
		if method == "sendMediaGroup":
			return [self._message(params, photo=self._photo()) for _ in params.get("media", [])]
		if method == "sendLocation":
			location = {"latitude": params["latitude"], "longitude": params["longitude"]}
			return self._message(params, location=location)
		if method.startswith(("send", "edit")):
			return self._message(params)
		return True

	def requests(self, method: str) -> list[dict[str, Any]]:
		"""Параметры всех вызовов указанного метода."""
		return [call.params for call in self.calls if call.method == method]

	def messages(self, chat_id: int | None = None) -> list[dict[str, Any]]:
		"""Все отправленные текстовые сообщения (в указанный чат)."""
		return [
			params
			for params in self.requests("sendMessage")
			if chat_id is None or params.get("chat_id") == chat_id
		]

	def message_with_text(self, text: str) -> dict[str, Any]:
		"""Последнее отправленное сообщение с этим текстом."""
		matches = [params for params in self.messages() if params.get("text") == text]
		sent = [params.get("text") for params in self.messages()]
		assert matches, f"Бот не отправил {text!r}. Отправлено: {sent}"
		return matches[-1]

	def reset(self) -> None:
		self.calls.clear()


def reply_keyboard_labels(params: dict[str, Any]) -> list[str]:
	"""Подписи reply-кнопок, отправленных вместе с сообщением."""
	markup = params.get("reply_markup") or {}
	return [button["text"] for row in markup.get("keyboard", []) for button in row]


def inline_buttons(params: dict[str, Any]) -> list[dict[str, Any]]:
	"""Инлайн-кнопки, отправленные вместе с сообщением."""
	markup = params.get("reply_markup") or {}
	return [button for row in markup.get("inline_keyboard", []) for button in row]


@asynccontextmanager
async def running_bot(api: FakeBotApi):
	"""Запускает настоящее приложение бота поверх поддельного Bot API.

	Падает, если во время работы хотя бы один обработчик выбросил исключение.
	"""
	application = build_application(request=api)
	errors: list[BaseException] = []

	async def collect_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
		errors.append(context.error)

	application.add_error_handler(collect_error)
	await application.initialize()
	await application.start()
	try:
		yield application
	finally:
		await application.stop()
		await application.shutdown()
	assert not errors, f"Необработанные ошибки в обработчиках: {errors!r}"


class ChatSimulator:
	"""Пользователь, переписывающийся с ботом в личном чате."""

	def __init__(
		self,
		application: Application,
		user_id: int = 7,
		first_name: str = "Тест",
		language_code: str | None = None,
	) -> None:
		self.application = application
		self.user = {"id": user_id, "is_bot": False, "first_name": first_name}
		if language_code:
			self.user["language_code"] = language_code
		self.chat = {"id": user_id, "type": "private", "first_name": first_name}
		self._ids = itertools.count(1)

	@property
	def user_id(self) -> int:
		return self.user["id"]

	async def process(self, payload: dict[str, Any]) -> None:
		payload["update_id"] = next(self._ids)
		await self.application.process_update(Update.de_json(payload, self.application.bot))

	def _message(self, **content: Any) -> dict[str, Any]:
		return {
			"message_id": next(self._ids),
			"date": MESSAGE_DATE,
			"chat": self.chat,
			"from": self.user,
			**content,
		}

	async def send(self, text: str) -> None:
		content: dict[str, Any] = {"text": text}
		if text.startswith("/"):
			command_length = len(text.split(maxsplit=1)[0])
			content["entities"] = [{"type": "bot_command", "offset": 0, "length": command_length}]
		await self.process({"message": self._message(**content)})

	async def edit(self, text: str) -> None:
		await self.process({"edited_message": {**self._message(text=text), "edit_date": MESSAGE_DATE}})

	async def share_contact(self, phone_number: str = "+998901234567") -> None:
		contact = {"phone_number": phone_number, "first_name": self.user["first_name"], "user_id": self.user_id}
		await self.process({"message": self._message(contact=contact)})

	async def press(self, callback_data: str) -> None:
		bot_message = {
			"message_id": next(self._ids),
			"date": MESSAGE_DATE,
			"chat": self.chat,
			"from": BOT_USER,
			"text": "…",
		}
		await self.process(
			{
				"callback_query": {
					"id": str(next(self._ids)),
					"from": self.user,
					"chat_instance": "test",
					"data": callback_data,
					"message": bot_message,
				}
			}
		)

	async def join_subscription_group(self) -> None:
		await self.process(
			{
				"chat_member": {
					"chat": SUBSCRIPTION_GROUP,
					"from": self.user,
					"date": MESSAGE_DATE,
					"old_chat_member": {"status": "left", "user": self.user},
					"new_chat_member": {"status": "member", "user": self.user},
				}
			}
		)


async def send_group_reply(
	application: Application,
	chat_id: int,
	from_user_id: int,
	reply_to_message_id: int,
	text: str,
) -> None:
	"""Сообщение администратора в служебной группе, отправленное ответом (Reply)."""
	chat = {"id": chat_id, "type": "supergroup", "title": "Служебная группа"}
	payload = {
		"update_id": 10_000 + reply_to_message_id,
		"message": {
			"message_id": 50_000 + reply_to_message_id,
			"date": MESSAGE_DATE,
			"chat": chat,
			"from": {"id": from_user_id, "is_bot": False, "first_name": "Admin"},
			"text": text,
			"reply_to_message": {
				"message_id": reply_to_message_id,
				"date": MESSAGE_DATE,
				"chat": chat,
				"from": BOT_USER,
				"text": "Обращение",
			},
		},
	}
	await application.process_update(Update.de_json(payload, application.bot))

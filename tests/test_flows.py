"""Сквозные сценарии: настоящее приложение бота поверх поддельного Bot API."""

from __future__ import annotations

import asyncio

from bot.app import _post_init
from bot.config import (
	SUBSCRIPTION_GROUP_URL,
	get_lawyer_reviews_chat_id,
	get_support_chat_id,
)
from bot.content.colonies import COLONY_COORDINATES, COLONY_GROUPS, HOTEL_INFO
from bot.content.texts import (
	ADDITIONAL_INFO_BUTTONS,
	COLONY_PROMPTS,
	HELP_TEXTS,
	LANGUAGE_BUTTONS,
	LAWYER_PHOTO_MISSING_TEXTS,
	LAWYER_REVIEW_SUCCESS_TEXTS,
	MAIN_GROUP_BUTTONS,
	MAIN_GROUP_LINK_PROMPTS,
	MENU_SECTION_TEXTS,
	MONEY_TRANSFER_DONE_TEXTS,
	MONEY_TRANSFER_PROMPT_TEXTS,
	PHONE_PROMPTS,
	START_TEXTS,
	SUBSCRIPTION_BUTTONS,
	SUBSCRIPTION_PROMPTS,
	SUBSCRIPTION_WELCOME_TEXTS,
	SUPPORT_BUTTON_TEXT,
	SUPPORT_PROMPTS,
	SUPPORT_SUCCESS_TEXTS,
	UNKNOWN_TEXT_REPLIES,
	colony_action_button_texts,
)
from bot.database import (
	get_lawyer_reviews,
	get_user_phone_number,
	register_user,
	save_user_language,
	save_user_phone_number,
)
from bot.keyboards import MENU_SECTION_BUTTONS
from tests.telegram_stub import (
	ChatSimulator,
	FakeBotApi,
	inline_buttons,
	reply_keyboard_labels,
	running_bot,
	send_group_reply,
)

RUSSIAN = next(label for label, code in LANGUAGE_BUTTONS if code == "ru")
INFO_SECTION, SERVICES_SECTION, BACK = MENU_SECTION_BUTTONS["ru"]
LOCATION, DIRECTORY, APPLICATION = colony_action_button_texts("ru")
HOTEL, SHOP, TAXI, LAWYERS, MONEY_TRANSFER, ADDITIONAL_INFO, _ = ADDITIONAL_INFO_BUTTONS["ru"]
NO_DATA = "📭 Данных нет"
MAIN_MENU = "Главное меню"
INFO_SCREEN = MENU_SECTION_TEXTS["ru"]["info"].splitlines()[-1]
SUBSCRIPTION_PROMPT = SUBSCRIPTION_PROMPTS["ru"].format(
	join=SUBSCRIPTION_BUTTONS["ru"][0],
	check=SUBSCRIPTION_BUTTONS["ru"][1],
)


def colony_index(colony_group: str) -> int:
	return COLONY_GROUPS.index(colony_group)


async def onboard(chat: ChatSimulator, api: FakeBotApi, colony: int = 0) -> None:
	"""Новый пользователь: /start → язык → телефон → колония."""
	await chat.send("/start")
	await chat.send(RUSSIAN)
	await chat.share_contact()
	await chat.press(f"colonies:select:{colony}")
	api.reset()


def test_new_user_goes_from_start_to_colony_location_step_by_step():
	async def scenario():
		api = FakeBotApi()
		async with running_bot(api) as application:
			chat = ChatSimulator(application)

			await chat.send("/start")
			greeting = api.message_containing(START_TEXTS["ru"])
			assert greeting["text"].startswith("<b>Шаг 1 из 3</b>")
			assert RUSSIAN in reply_keyboard_labels(greeting)

			await chat.send(RUSSIAN)
			phone_step = api.message_containing(PHONE_PROMPTS["ru"]["prompt"])
			assert "<b>Шаг 2 из 3</b>" in phone_step["text"]
			assert phone_step["reply_markup"]["keyboard"][0][0]["request_contact"] is True

			await chat.share_contact("+998901112233")
			assert get_user_phone_number(chat.user_id) == "+998901112233"
			colony_step = api.message_containing(COLONY_PROMPTS["ru"])
			assert "<b>Шаг 3 из 3</b>" in colony_step["text"]
			assert "colonies:select:0" in [button["callback_data"] for button in inline_buttons(colony_step)]

			await chat.press("colonies:select:0")
			assert api.requests("editMessageText")
			main_menu = api.message_containing(MAIN_MENU)
			assert INFO_SECTION in reply_keyboard_labels(main_menu)
			assert main_menu["reply_markup"]["input_field_placeholder"] == "Выберите раздел"

			api.reset()
			await chat.send(INFO_SECTION)
			assert LOCATION in reply_keyboard_labels(api.message_containing(INFO_SCREEN))

			await chat.send(LOCATION)
			(location,) = api.requests("sendLocation")
			assert location["latitude"] == COLONY_COORDINATES[COLONY_GROUPS[0]][0]

	asyncio.run(scenario())


def test_bot_requires_group_membership_and_continues_after_check_button():
	async def scenario():
		api = FakeBotApi()
		api.member_status = "left"
		async with running_bot(api) as application:
			chat = ChatSimulator(application)
			await chat.send("/start")
			await chat.send(RUSSIAN)
			buttons = inline_buttons(api.message_with_text(SUBSCRIPTION_PROMPT))
			assert buttons[0]["url"] == SUBSCRIPTION_GROUP_URL
			assert buttons[1]["callback_data"] == "subscription:check"

			api.reset()
			await chat.send(INFO_SECTION)
			assert [params["text"] for params in api.messages()] == [SUBSCRIPTION_PROMPT]

			api.member_status = "member"
			await chat.press("subscription:check")
			welcome = api.message_containing(SUBSCRIPTION_WELCOME_TEXTS["ru"])
			assert PHONE_PROMPTS["ru"]["prompt"] in welcome["text"]

			# Контакт приходит вне диалога выбора языка — его всё равно нужно принять.
			await chat.share_contact()
			assert get_user_phone_number(chat.user_id) == "+998901234567"
			api.message_containing(COLONY_PROMPTS["ru"])

	asyncio.run(scenario())


def test_joining_the_group_continues_onboarding():
	async def scenario():
		api = FakeBotApi()
		api.member_status = "left"
		async with running_bot(api) as application:
			chat = ChatSimulator(application)
			await chat.send("/start")
			await chat.send(RUSSIAN)

			api.reset()
			api.member_status = "member"
			await chat.join_subscription_group()
			(welcome,) = api.messages(chat.user_id)
			assert SUBSCRIPTION_WELCOME_TEXTS["ru"] in welcome["text"]
			assert PHONE_PROMPTS["ru"]["prompt"] in welcome["text"]

	asyncio.run(scenario())


def test_support_request_reaches_group_and_admin_reply_reaches_user():
	async def scenario():
		api = FakeBotApi()
		async with running_bot(api) as application:
			chat = ChatSimulator(application)
			await onboard(chat, api)

			await chat.send(SUPPORT_BUTTON_TEXT["ru"])
			api.message_containing(SUPPORT_PROMPTS["ru"])
			await chat.send("Не приходит перевод")

			support_chat_id = get_support_chat_id()
			(report,) = api.messages(support_chat_id)
			assert "Не приходит перевод" in report["text"]
			assert f"Telegram ID: {chat.user_id}" in report["text"]
			assert "+998901234567" in report["text"]
			# После отправки обращения пользователь снова видит меню колонии.
			assert INFO_SECTION in reply_keyboard_labels(api.message_with_text(SUPPORT_SUCCESS_TEXTS["ru"]))

			report_message_id = next(
				call.result["message_id"]
				for call in api.calls
				if call.method == "sendMessage" and call.params["chat_id"] == support_chat_id
			)
			await send_group_reply(application, support_chat_id, 1, report_message_id, "Проверим")
			(copy,) = api.requests("copyMessage")
			assert copy["chat_id"] == chat.user_id
			assert api.messages(support_chat_id)[-1]["text"] == "✅ Ответ отправлен пользователю."

	asyncio.run(scenario())


def test_start_command_leaves_support_dialog():
	async def scenario():
		api = FakeBotApi()
		async with running_bot(api) as application:
			chat = ChatSimulator(application)
			await onboard(chat, api)

			await chat.send(SUPPORT_BUTTON_TEXT["ru"])
			await chat.send("/start")
			api.message_containing(START_TEXTS["ru"])
			await chat.send("просто текст")

			assert api.messages(get_support_chat_id()) == []
			api.message_with_text(UNKNOWN_TEXT_REPLIES["ru"])

	asyncio.run(scenario())


def test_edited_message_is_not_sent_to_support_again():
	async def scenario():
		api = FakeBotApi()
		async with running_bot(api) as application:
			chat = ChatSimulator(application)
			await onboard(chat, api)

			await chat.send(SUPPORT_BUTTON_TEXT["ru"])
			await chat.edit("исправленный старый текст")
			assert api.messages(get_support_chat_id()) == []

			await chat.send("Новое обращение")
			assert len(api.messages(get_support_chat_id())) == 1

	asyncio.run(scenario())


def test_lawyer_review_ignores_menu_buttons_and_publishes_real_text():
	async def scenario():
		api = FakeBotApi()
		async with running_bot(api) as application:
			chat = ChatSimulator(application)
			await onboard(chat, api)

			await chat.send(SERVICES_SECTION)
			await chat.send(LAWYERS)
			region_buttons = inline_buttons(api.messages()[-1])
			assert "lawyer:region:tashkent_city" in [button["callback_data"] for button in region_buttons]

			await chat.press("lawyer:region:tashkent_city")
			await chat.press("lawyer:profile:tima")
			# Фото адвоката пока нет — карточка приходит текстом с пометкой «данных нет».
			profile = api.messages()[-1]
			assert "<b>Тима</b>" in profile["text"]
			assert LAWYER_PHOTO_MISSING_TEXTS["ru"] in profile["text"]
			await chat.press("lawyer:write_review:tima")

			# Пользователь передумал и нажал кнопку меню — это не отзыв.
			await chat.send(BACK)
			assert get_lawyer_reviews("tima") == []
			assert api.messages(get_lawyer_reviews_chat_id()) == []

			await chat.press("lawyer:write_review:tima")
			await chat.send("Помог быстро и вежливо")
			((review, _created_at, _author),) = get_lawyer_reviews("tima")
			assert review == "Помог быстро и вежливо"
			(published,) = api.messages(get_lawyer_reviews_chat_id())
			assert "Помог быстро и вежливо" in published["text"]
			api.message_with_text(LAWYER_REVIEW_SUCCESS_TEXTS["ru"])

	asyncio.run(scenario())


def test_missing_data_is_reported_as_no_data():
	no_hotel = "SmartJIEK10"
	hotel_phone_only = "SmartJIEK13"
	no_directory_contacts = "SmartJIEK20"
	assert HOTEL_INFO[no_hotel] == ((), "")
	assert not HOTEL_INFO[hotel_phone_only][0] and HOTEL_INFO[hotel_phone_only][1]

	async def scenario():
		api = FakeBotApi()
		async with running_bot(api) as application:
			chat = ChatSimulator(application)
			await onboard(chat, api, colony=colony_index(no_hotel))

			await chat.send(SERVICES_SECTION)
			for button in (SHOP, TAXI):
				await chat.send(button)
				assert api.messages()[-1]["text"] == f"<b>{button}</b>\n\n{NO_DATA}"

			await chat.send(BACK)
			await chat.send(INFO_SECTION)
			await chat.send(HOTEL)
			assert api.messages()[-1]["text"].endswith(NO_DATA)

			await chat.press(f"colonies:select:{colony_index(hotel_phone_only)}")
			api.reset()
			await chat.send(INFO_SECTION)
			await chat.send(HOTEL)
			card = api.messages()[-1]["text"]
			assert "📍 Локация: данных нет" in card
			assert HOTEL_INFO[hotel_phone_only][1] in card
			assert api.requests("sendLocation") == []

			await chat.press(f"colonies:select:{colony_index(no_directory_contacts)}")
			await chat.send(INFO_SECTION)
			await chat.send(DIRECTORY)
			assert "Контакты 20-й колонии:\n" + NO_DATA in api.messages()[-1]["text"]

	asyncio.run(scenario())


def test_money_transfer_instructions_are_uploaded_once_then_reused():
	async def scenario():
		api = FakeBotApi()
		async with running_bot(api) as application:
			chat = ChatSimulator(application)
			await onboard(chat, api)

			await chat.send(SERVICES_SECTION)
			await chat.send(MONEY_TRANSFER)
			api.message_with_text(MONEY_TRANSFER_PROMPT_TEXTS["ru"])

			await chat.press("money_transfer:yes")
			uploads = [call for call in api.calls if call.method == "sendVideo"]
			assert len(uploads) == 3
			assert all("video" not in call.params for call in uploads)  # файлы загружались с диска
			assert [params["action"] for params in api.requests("sendChatAction")] == ["upload_video"] * 3
			api.message_with_text(MONEY_TRANSFER_DONE_TEXTS["ru"])

			api.reset()
			await chat.press("money_transfer:yes")
			assert [params["video"] for params in api.requests("sendVideo")] == [
				call.result["video"]["file_id"] for call in uploads
			]

	asyncio.run(scenario())


def test_additional_info_album_is_uploaded_once_then_reused():
	async def scenario():
		api = FakeBotApi()
		async with running_bot(api) as application:
			chat = ChatSimulator(application)
			await onboard(chat, api)

			await chat.send(INFO_SECTION)
			await chat.send(ADDITIONAL_INFO)
			(first_album,) = api.requests("sendMediaGroup")
			assert all(item["media"].startswith("attach://") for item in first_album["media"])

			api.reset()
			await chat.send(ADDITIONAL_INFO)
			(second_album,) = api.requests("sendMediaGroup")
			assert all(item["media"].startswith("photo-") for item in second_album["media"])

	asyncio.run(scenario())


def test_user_state_survives_bot_restart():
	async def scenario():
		api = FakeBotApi()
		async with running_bot(api) as application:
			await onboard(ChatSimulator(application), api)

		api = FakeBotApi()
		async with running_bot(api) as application:
			await ChatSimulator(application).send(INFO_SECTION)
			assert LOCATION in reply_keyboard_labels(api.message_containing(INFO_SCREEN))
			assert not [params for params in api.messages() if START_TEXTS["ru"] in params["text"]]

	asyncio.run(scenario())


def test_existing_user_with_old_keyboard_is_asked_to_pick_colony_after_update():
	"""Первый запуск новой версии: язык и телефон есть только в базе, колонии в памяти нет."""
	register_user(7, None, "Тест", None)
	save_user_language(7, "uz")
	save_user_phone_number(7, "+998901234567")

	async def scenario():
		api = FakeBotApi()
		async with running_bot(api) as application:
			await ChatSimulator(application).send(INFO_SECTION)  # кнопка со старой русской клавиатуры
			colony_prompt = api.message_with_text(COLONY_PROMPTS["uz"])
			assert inline_buttons(colony_prompt)

	asyncio.run(scenario())


def test_greeting_uses_telegram_language_for_new_users():
	async def scenario():
		api = FakeBotApi()
		async with running_bot(api) as application:
			await ChatSimulator(application, language_code="uz").send("/start")
			api.message_containing(START_TEXTS["uz"])
			await ChatSimulator(application, user_id=8, language_code="en").send("/start")
			api.message_containing(START_TEXTS["ru"])

	asyncio.run(scenario())


def test_help_explains_sections_with_real_button_names():
	async def scenario():
		api = FakeBotApi()
		async with running_bot(api) as application:
			chat = ChatSimulator(application)
			await onboard(chat, api)
			await chat.send("/help")
			help_message = api.message_containing(HELP_TEXTS["ru"]["title"])
			assert f"<b>{SUPPORT_BUTTON_TEXT['ru']}</b>" in help_message["text"]
			assert INFO_SECTION in reply_keyboard_labels(help_message)

	asyncio.run(scenario())


def test_main_group_button_works_in_every_language():
	"""Подпись кнопки на любом языке должна открывать ссылку на основную группу."""
	async def scenario():
		api = FakeBotApi()
		async with running_bot(api) as application:
			for index, language in enumerate(("ru", "uz", "uz_cyr")):
				chat = ChatSimulator(application, user_id=7 + index)
				await chat.send("/start")
				await chat.send(dict((code, label) for label, code in LANGUAGE_BUTTONS)[language])
				await chat.share_contact()
				await chat.press("colonies:select:0")

				api.reset()
				await chat.send(MAIN_GROUP_BUTTONS[language])
				message = api.messages()[-1]
				assert message["text"] == MAIN_GROUP_LINK_PROMPTS[language]
				(button,) = inline_buttons(message)
				assert button["url"] == SUBSCRIPTION_GROUP_URL

	asyncio.run(scenario())


def test_bot_commands_are_registered_in_russian_and_uzbek():
	async def scenario():
		api = FakeBotApi()
		async with running_bot(api) as application:
			await _post_init(application)
		descriptions = {
			params.get("language_code"): [command["description"] for command in params["commands"]]
			for params in api.requests("setMyCommands")
		}
		assert descriptions == {
			None: ["Запустить бота", "Выбрать язык и колонию", "Как пользоваться ботом"],
			"uz": ["Botni ishga tushirish", "Til va koloniyani tanlash", "Botdan foydalanish yo'riqnomasi"],
		}

	asyncio.run(scenario())

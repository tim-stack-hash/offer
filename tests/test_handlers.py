"""Сценарии обработчиков с поддельными объектами Telegram."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from telegram.ext import ConversationHandler

from bot.content.texts import ADDITIONAL_INFO_BUTTONS, COLONY_LOCATION_BUTTONS
from bot.database import get_lawyer_reviews
from bot.handlers import feedback, lawyer
from bot.handlers.colony import menu


def _update(text: str, user_id: int = 7):
	message = MagicMock()
	message.text = text
	message.reply_text = AsyncMock()
	message.chat_id = user_id
	user = SimpleNamespace(id=user_id, username=None, first_name="Test", last_name=None, is_bot=False)
	return SimpleNamespace(
		message=message,
		effective_message=message,
		effective_user=user,
		effective_chat=SimpleNamespace(id=user_id, type="private"),
		callback_query=None,
	)


def _context(**user_data):
	return SimpleNamespace(user_data=dict(user_data), bot=MagicMock())


def test_menu_button_cancels_pending_lawyer_review():
	update = _update(COLONY_LOCATION_BUTTONS["ru"])
	context = _context(language="ru", pending_lawyer_review="tima")

	handled = asyncio.run(lawyer.handle_lawyer_review_text(update, context))

	assert handled is False
	assert "pending_lawyer_review" not in context.user_data
	assert get_lawyer_reviews("tima") == []


def test_lawyers_button_opens_regions_instead_of_stub():
	update = _update(ADDITIONAL_INFO_BUTTONS["ru"][3])
	context = _context(language="ru", colony="SmartJIEK1")

	asyncio.run(menu.handle_menu_text(update, context))

	reply_markup = update.message.reply_text.call_args.kwargs["reply_markup"]
	callbacks = [button.callback_data for row in reply_markup.inline_keyboard for button in row]
	assert all(data.startswith("lawyer:region:") for data in callbacks)


def test_unknown_text_gets_a_hint():
	update = _update("какой-то текст")
	context = _context(language="ru", colony="SmartJIEK1", phone_number="+998901234567")

	asyncio.run(menu.handle_menu_text(update, context))

	update.message.reply_text.assert_awaited_once()
	assert update.message.reply_text.call_args.args[0] == menu.UNKNOWN_TEXT_REPLIES["ru"]


def test_menu_labels_have_no_conflicts_and_cover_all_languages():
	for language, buttons in ADDITIONAL_INFO_BUTTONS.items():
		for label in buttons[:-1]:  # последняя кнопка — WebApp my.gov
			assert label.strip() in menu.MENU_ACTIONS, (language, label)


def test_feedback_failure_keeps_user_in_message_step(monkeypatch):
	monkeypatch.setattr(feedback, "forward_user_report", AsyncMock(return_value=False))
	update = _update("Предложение")
	context = _context(language="ru", feedback_category="proposal")

	state = asyncio.run(feedback.send_feedback_message(update, context))

	assert state == feedback.FEEDBACK_MESSAGE
	assert state != ConversationHandler.END

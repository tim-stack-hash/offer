"""Прочие клавиатуры: основная группа, группа с одеждой, панель администратора."""

from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.config import PAYNET_APP_URL, UZUM_BANK_APP_URL
from bot.content.texts import (
	MAIN_GROUP,
	MAIN_GROUP_BUTTONS,
	MONEY_TRANSFER_NO_BUTTONS,
	MONEY_TRANSFER_YES_BUTTONS,
)


def money_transfer_apps_keyboard() -> InlineKeyboardMarkup:
	"""Показывает ссылки Google Play на приложения для перевода денег."""
	return InlineKeyboardMarkup(
		[
			[
				InlineKeyboardButton("📲 Paynet", url=PAYNET_APP_URL),
				InlineKeyboardButton("💳 Uzum Bank", url=UZUM_BANK_APP_URL),
			],
		]
	)


def money_transfer_confirmation_keyboard(language: str) -> InlineKeyboardMarkup:
	"""Показывает кнопки подтверждения отправки инструкций по переводу."""
	return InlineKeyboardMarkup(
		[[
			InlineKeyboardButton(
				MONEY_TRANSFER_YES_BUTTONS.get(language, MONEY_TRANSFER_YES_BUTTONS["ru"]),
				callback_data="money_transfer:yes",
			),
			InlineKeyboardButton(
				MONEY_TRANSFER_NO_BUTTONS.get(language, MONEY_TRANSFER_NO_BUTTONS["ru"]),
				callback_data="money_transfer:no",
			),
		]]
	)


def main_group_link_keyboard(language: str) -> InlineKeyboardMarkup:
	"""Инлайн-кнопка со ссылкой на основную (не колониальную) группу."""
	button_text = MAIN_GROUP_BUTTONS.get(language, MAIN_GROUP_BUTTONS["ru"])
	group_url = f"https://t.me/{MAIN_GROUP[1].removeprefix('@')}"
	return InlineKeyboardMarkup(
		[[InlineKeyboardButton(button_text, url=group_url)]]
	)


def admin_panel_keyboard() -> InlineKeyboardMarkup:
	"""Кнопки списка пользователей и перехода к панели активности."""
	return InlineKeyboardMarkup(
		[
			[InlineKeyboardButton("📥 Скачать список пользователей (CSV)", callback_data="admin:export")],
			[InlineKeyboardButton("📊 Панель активности (/admin2)", callback_data="admin:activity")],
		]
	)


def admin_activity_keyboard() -> InlineKeyboardMarkup:
	"""Кнопки выгрузки сводки и полной истории нажатий."""
	return InlineKeyboardMarkup(
		[
			[InlineKeyboardButton("📊 Скачать счётчики и последние нажатия (CSV)", callback_data="admin:activity_export")],
			[InlineKeyboardButton("🕒 Скачать историю всех нажатий (CSV)", callback_data="admin:activity_history_export")],
		]
	)

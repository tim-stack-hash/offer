"""Команда /admin и выгрузка списка пользователей в CSV — доступны только администраторам."""

from __future__ import annotations

from telegram import InputFile, Update
from telegram.ext import ContextTypes

from bot.config import is_admin
from bot.database import (
	export_user_activity_history_csv,
	export_user_activity_csv,
	export_users_csv,
	get_activity_summary,
	get_user_count,
)
from bot.keyboards import admin_activity_keyboard, admin_panel_keyboard


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Команда /admin: показывает число пользователей и кнопку выгрузки CSV (только в личном чате с админом)."""
	user = update.effective_user
	message = update.effective_message
	if not user or not message:
		return
	if not is_admin(user.id):
		await message.reply_text("⛔ Доступ к панели администратора запрещён.")
		return
	if update.effective_chat and update.effective_chat.type != "private":
		await message.reply_text("Откройте личный чат с ботом и отправьте /admin.")
		return

	await message.reply_text(
		f"👥 Пользователей: {get_user_count()}\n"
		"Выгрузка содержит имя, username и только те номера, "
		"которые пользователи отправили боту самостоятельно.",
		reply_markup=admin_panel_keyboard(),
	)


async def admin_activity_panel(
	update: Update,
	context: ContextTypes.DEFAULT_TYPE,
) -> None:
	"""Команда /admin2: показывает сводку нажатий и выгрузку активности по пользователям."""
	user = update.effective_user
	message = update.effective_message
	if not user or not message:
		return
	if not is_admin(user.id):
		await message.reply_text("⛔ Доступ к панели администратора запрещён.")
		return
	if update.effective_chat and update.effective_chat.type != "private":
		await message.reply_text("Откройте личный чат с ботом и отправьте /admin2.")
		return

	await message.reply_text(
		_activity_summary_text(),
		reply_markup=admin_activity_keyboard(),
	)


def _activity_summary_text() -> str:
	"""Формирует краткую статистику по числу кликов и популярным кнопкам."""
	users_count, clicks_count, top_actions = get_activity_summary()
	lines = [
		"📊 Панель активности пользователей",
		f"👥 Пользователей с действиями: {users_count}",
		f"🖱 Всего нажатий: {clicks_count}",
	]
	if top_actions:
		lines.append("\n🔝 Популярные кнопки:")
		lines.extend(f"• {action}: {count}" for action, count in top_actions)
	else:
		lines.append("\nПока действий нет.")
	lines.append(
		"\nВыгрузка содержит имя, username, телефон (если пользователь поделился) "
		"и количество нажатий по каждой кнопке. Полная история хранит дату и время каждого нажатия (UTC+05:00)."
	)
	return "\n".join(lines)


async def handle_admin_callback(
	update: Update,
	context: ContextTypes.DEFAULT_TYPE,
) -> None:
	"""Обрабатывает нажатие кнопки «Скачать список пользователей (CSV)» в панели администратора."""
	query = update.callback_query
	user = update.effective_user
	if not query or not user:
		return
	if not is_admin(user.id):
		await query.answer("⛔ Доступ запрещён.", show_alert=True)
		return
	if not update.effective_chat or update.effective_chat.type != "private":
		await query.answer("Откройте личный чат с ботом.", show_alert=True)
		return

	await query.answer()
	if query.data == "admin:activity":
		if query.message:
			await query.message.reply_text(
				_activity_summary_text(),
				reply_markup=admin_activity_keyboard(),
			)
	elif query.data == "admin:activity_export":
		document = export_user_activity_csv()
		await context.bot.send_document(
			chat_id=update.effective_chat.id,
			document=InputFile(document, filename="user_activity.csv"),
			caption="📊 Счётчики нажатий и время последнего нажатия каждой кнопки.",
		)
	elif query.data == "admin:activity_history_export":
		document = export_user_activity_history_csv()
		await context.bot.send_document(
			chat_id=update.effective_chat.id,
			document=InputFile(document, filename="user_activity_history.csv"),
			caption="🕒 История нажатий: отдельная строка для каждого события, время UTC+05:00.",
		)
	elif query.data == "admin:export":
		document = export_users_csv()
		await context.bot.send_document(
			chat_id=update.effective_chat.id,
			document=InputFile(document, filename="bot_users.csv"),
			caption=f"👥 Пользователей: {get_user_count()}",
		)

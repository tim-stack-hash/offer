"""Тексты меню колонии: выбор/смена колонии, подписи кнопок и формирование их с номером колонии."""

from __future__ import annotations

import re

# Подпись кнопки «Поменять колонию».
CHANGE_COLONY_BUTTONS = {
	"ru": "🏢 Поменять колонию",
	"uz": "🏢 Koloniyani o'zgartirish",
	"uz_cyr": "🏢 Колонияни ўзгартириш",
}

# Текст приглашения выбрать колонию.
COLONY_PROMPTS = {
	"ru": "🏢 Выберите колонию 👇",
	"uz": "🏢 Koloniyani tanlang 👇",
	"uz_cyr": "🏢 Колонияни танланг 👇",
}

# Текст подтверждения выбранной колонии.
COLONY_SELECTED_TEXTS = {
	"ru": "✅ Вы выбрали:",
	"uz": "✅ Siz tanladingiz:",
	"uz_cyr": "✅ Сиз танладингиз:",
}

# Подпись кнопки перехода в группу колонии.
COLONY_GROUP_BUTTONS = {
	"ru": "💬 Родительская группа",
	"uz": "💬 Ota-Onalar guruhi",
	"uz_cyr": "💬 Ота-Оналар гурухи",
}

# Текст приглашения открыть группу колонии.
COLONY_GROUP_LINK_PROMPTS = {
	"ru": "👇 Нажмите кнопку ниже, чтобы открыть группу колонии:",
	"uz": "👇 Koloniya guruhini ochish uchun quyidagi tugmani bosing:",
	"uz_cyr": "👇 Колония гуруҳини очиш учун қуйидаги тугмани босинг:",
}


# Подпись кнопки «Основная группа».
MAIN_GROUP_BUTTONS = {
	"ru":     "💬 Группа проверки денег",
	"uz":     "💬 Pul tushumlari guruhi",
	"uz_cyr": "💬 Пул тушумлари гурухи",
}

# Текст приглашения открыть основную группу.
MAIN_GROUP_LINK_PROMPTS = {
	"ru": "👇 Нажмите кнопку ниже, чтобы открыть группу проверки отправленных денег:",
	"uz": "👇 Pul tushumlari guruhni ochish uchun quyidagi tugmani bosing:",
	"uz_cyr": "👇 Пул тушумлари гурухини очиш учун қуйидаги тугмани босинг:",
}

# Подпись кнопки «Локация» (используется при формировании текста кнопок колонии).
COLONY_LOCATION_BUTTONS = {
	"ru": "📍 Локация",
	"uz": "📍 Lokatsiya",
	"uz_cyr": "📍 Локация",
}

# Подпись кнопки «Справочник» (устаревший вариант без номера колонии).
COLONY_DIRECTORY_BUTTONS = {
	"ru": "📚 Справочник",
	"uz": "📚 Ma'lumotnoma",
	"uz_cyr": "📚 Маълумотнома",
}

# Подпись кнопки «Образцы заявлений» (устаревший вариант без номера колонии).
COLONY_APPLICATION_BUTTONS = {
	"ru": "📄 Образцы заявлений",
	"uz": "📄 Ariza nusxalari",
	"uz_cyr": "📄 Ариза нусхалари",
}

# Текст выбора срока свидания и подписи кнопок с образцами заявлений.
APPLICATION_TYPE_PROMPTS = {
	"ru": "👇 Выберите тип заявления:",
	"uz": "👇 Ariza turini tanlang:",
	"uz_cyr": "👇 Ариза турини танланг:",
}
APPLICATION_TYPE_BUTTONS = {
	"ru": ("Длительное\nсвидание", "Краткосрочное\nсвидание"),
	"uz": ("Uzoq muddatli", "Qisqa muddatli"),
	"uz_cyr": ("Узоқ муддатли", "Қисқа муддатли"),
}

# Подпись и телеграм-юзернейм основной (не колониальной) группы.
MAIN_GROUP = ("💬 Группа проверки денег", "smartdunyopaygroup")


# Подпись перед отправкой локации выбранной колонии.
COLONY_LOCATION_PROMPTS = {
	"ru": "📍 Локация {colony}-й колонии:",
	"uz": "📍 «{colony}» koloniyasining joylashuvi:",
	"uz_cyr": "📍 «{colony}» колониясининг жойлашуви:",
}

# Суффиксы названий кнопок «локация/справочник/заявления» для каждого языка.
COLONY_ACTION_SUFFIXES = {
	"ru": ("Локация", "Справочник", "Заявления"),
	"uz": ("Lokatsiya", "Ma'lumotnoma", "Arizalar"),
	"uz_cyr": ("Локация", "Маълумотнома", "Аризалар"),
}


def colony_action_button_texts(language: str) -> tuple[str, str, str]:
	"""Подписи кнопок «локация / справочник / заявления» в меню колонии."""
	location_suffix, directory_suffix, application_suffix = COLONY_ACTION_SUFFIXES.get(
		language,
		COLONY_ACTION_SUFFIXES["ru"],
	)
	return (
		f"📍 {location_suffix}",
		f"📚 {directory_suffix}",
		f"📄 {application_suffix}",
	)


def colony_location_prompt(language: str, colony_name: str) -> str:
	"""Формирует подпись локации с кратким номером колонии на русском."""
	if language == "ru":
		colony_number = re.search(r"\d+", colony_name)
		colony_name = colony_number.group() if colony_number else colony_name
	return COLONY_LOCATION_PROMPTS.get(
		language,
		COLONY_LOCATION_PROMPTS["ru"],
	).format(colony=colony_name)


# Подпись под ссылкой на родительскую группу колонии.
GROUP_SELECTED_TEXTS = {
	"ru": "✅ Группа {number}-й колонии.",
	"uz": "✅ {number}-son koloniya guruhi.",
	"uz_cyr": "✅ {number}-сон колония гуруҳи.",
}

# Экраны меню колонии. {colony} — выбранная колония, {info} и {services} — кнопки разделов.
MENU_SECTION_TEXTS = {
	"ru": {
		"root": "🏠 <b>Главное меню</b> · {colony}\n\n{info} — локация, справочник, образцы заявлений, гостиница\n{services} — одежда, такси, адвокаты, перевод денег\n\nВыберите раздел 👇",
		"info": "{info} · {colony}\n\nВыберите, что вас интересует 👇",
		"services": "{services}\n\nВыберите услугу 👇",
	},
	"uz": {
		"root": "🏠 <b>Bosh menyu</b> · {colony}\n\n{info} — lokatsiya, ma'lumotnoma, ariza namunalari, mehmonxona\n{services} — kiyimlar, taksi, advokatlar, pul o'tkazish\n\nBo'limni tanlang 👇",
		"info": "{info} · {colony}\n\nKeraklisini tanlang 👇",
		"services": "{services}\n\nXizmatni tanlang 👇",
	},
	"uz_cyr": {
		"root": "🏠 <b>Бош меню</b> · {colony}\n\n{info} — локация, маълумотнома, ариза намуналари, меҳмонхона\n{services} — кийимлар, такси, адвокатлар, пул ўтказиш\n\nБўлимни танланг 👇",
		"info": "{info} · {colony}\n\nКераклисини танланг 👇",
		"services": "{services}\n\nХизматни танланг 👇",
	},
}

# Кнопки разделов меню колонии: «Информация», «Услуги» и возврат на главный экран.
MENU_SECTION_BUTTONS = {
	"ru": ("ℹ️ Информация", "🧰 Услуги", "⬅️ Назад"),
	"uz": ("ℹ️ Ma'lumot", "🧰 Xizmatlar", "⬅️ Orqaga"),
	"uz_cyr": ("ℹ️ Маълумот", "🧰 Хизматлар", "⬅️ Орқага"),
}

# Нажата кнопка колонии, которой больше нет в списке.
COLONY_NOT_FOUND_TEXTS = {
	"ru": "Колония не найдена.",
	"uz": "Koloniya topilmadi.",
	"uz_cyr": "Колония топилмади.",
}

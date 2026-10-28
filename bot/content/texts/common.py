"""Общие сообщения бота: ошибки, подсказки, непонятный ввод."""

from __future__ import annotations

# Необработанная ошибка: пользователь видит это вместо молчания.
ERROR_TEXTS = {
	"ru": "⚠️ Произошла ошибка. Попробуйте ещё раз или нажмите /start.",
	"uz": "⚠️ Xatolik yuz berdi. Qayta urinib ko'ring yoki /start ni bosing.",
	"uz_cyr": "⚠️ Хатолик юз берди. Қайта уриниб кўринг ёки /start ни босинг.",
}

# Нажата кнопка со старой или повреждённой клавиатуры.
UNKNOWN_ACTION_TEXTS = {
	"ru": "Неизвестное действие. Откройте меню заново.",
	"uz": "Noma'lum amal. Menyuni qaytadan oching.",
	"uz_cyr": "Номаълум амал. Менюни қайтадан очинг.",
}

# Пользователь написал текст, который бот не понимает.
UNKNOWN_TEXT_REPLIES = {
	"ru": "Пожалуйста, воспользуйтесь кнопками меню ниже 👇",
	"uz": "Iltimos, quyidagi menyu tugmalaridan foydalaning 👇",
	"uz_cyr": "Илтимос, қуйидаги меню тугмаларидан фойдаланинг 👇",
}

# Обращение или жалобу не удалось переслать в служебную группу.
DELIVERY_ERROR_TEXTS = {
	"ru": "⚠️ Не удалось отправить сообщение. Попробуйте ещё раз чуть позже.",
	"uz": "⚠️ Xabarni yuborib bo'lmadi. Birozdan so'ng qayta urinib ko'ring.",
	"uz_cyr": "⚠️ Хабарни юбориб бўлмади. Бироздан сўнг қайта уриниб кўринг.",
}

# Ответ на кнопку, по которой у бота нет информации.
NO_DATA_TEXTS = {
	"ru": "Данных нет",
	"uz": "Ma'lumot yo'q",
	"uz_cyr": "Маълумот йўқ",
}

# Номер шага первой настройки: язык → телефон → колония.
STEP_LABELS = {
	"ru": "Шаг {step} из 3",
	"uz": "{step}-qadam (3 tadan)",
	"uz_cyr": "{step}-қадам (3 тадан)",
}

# Подсказка в поле ввода, пока язык ещё не выбран.
LANGUAGE_PLACEHOLDER = "🌐 Выберите язык / Tilni tanlang"

# Подсказки в поле ввода под reply-клавиатурами (Telegram ограничивает их 64 символами).
KEYBOARD_PLACEHOLDERS = {
	"ru": {
		"phone": "Нажмите кнопку ниже 👇",
		"menu": "Выберите раздел",
		"info": "Что вас интересует?",
		"services": "Выберите услугу",
		"message": "Напишите сообщение…",
		"choice": "Выберите вариант",
	},
	"uz": {
		"phone": "Quyidagi tugmani bosing 👇",
		"menu": "Bo'limni tanlang",
		"info": "Sizni nima qiziqtiradi?",
		"services": "Xizmatni tanlang",
		"message": "Xabar yozing…",
		"choice": "Variantni tanlang",
	},
	"uz_cyr": {
		"phone": "Қуйидаги тугмани босинг 👇",
		"menu": "Бўлимни танланг",
		"info": "Сизни нима қизиқтиради?",
		"services": "Хизматни танланг",
		"message": "Хабар ёзинг…",
		"choice": "Вариантни танланг",
	},
}

# Справка /help. Названия кнопок подставляются из клавиатур, здесь — только пояснения.
HELP_TEXTS = {
	"ru": {
		"title": "❓ <b>Как пользоваться ботом</b>",
		"menu": "В главном меню два раздела:",
		"info": "локация и справочник колонии, образцы заявлений, гостиница, что можно передавать",
		"services": "одежда, такси, адвокаты, перевод денег",
		"colony_group": "группа родственников вашей колонии",
		"main_group": "проверка поступления отправленных денег",
		"support": "напишите вопрос, и оператор ответит в этом чате",
		"feedback": "расскажите, что нам улучшить",
		"commands": "/start — начать заново\n/menu — сменить язык и колонию\n/help — эта справка",
	},
	"uz": {
		"title": "❓ <b>Botdan qanday foydalaniladi</b>",
		"menu": "Bosh menyuda ikki bo'lim bor:",
		"info": "koloniya lokatsiyasi va ma'lumotnomasi, ariza namunalari, mehmonxona, nimalarni berish mumkinligi",
		"services": "kiyimlar, taksi, advokatlar, pul o'tkazish",
		"colony_group": "koloniyangiz bo'yicha ota-onalar guruhi",
		"main_group": "yuborilgan pul tushumini tekshirish",
		"support": "savolingizni yozing, operator shu chatda javob beradi",
		"feedback": "nimani yaxshilashimiz kerakligini yozing",
		"commands": "/start — qaytadan boshlash\n/menu — til va koloniyani o'zgartirish\n/help — ushbu yo'riqnoma",
	},
	"uz_cyr": {
		"title": "❓ <b>Ботдан қандай фойдаланилади</b>",
		"menu": "Бош менюда икки бўлим бор:",
		"info": "колония локацияси ва маълумотномаси, ариза намуналари, меҳмонхона, нималарни бериш мумкинлиги",
		"services": "кийимлар, такси, адвокатлар, пул ўтказиш",
		"colony_group": "колониянгиз бўйича ота-оналар гуруҳи",
		"main_group": "юборилган пул тушумини текшириш",
		"support": "саволингизни ёзинг, оператор шу чатда жавоб беради",
		"feedback": "нимани яхшилашимиз кераклигини ёзинг",
		"commands": "/start — қайтадан бошлаш\n/menu — тил ва колонияни ўзгартириш\n/help — ушбу йўриқнома",
	},
}

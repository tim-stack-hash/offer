"""Тексты запроса и сохранения номера телефона пользователя."""

from __future__ import annotations

PHONE_PROMPTS = {
	"ru": {
		"prompt": "📱 Нажмите кнопку ниже, чтобы отправить свой номер телефона и продолжить.",
		"retry": "📱 Пожалуйста, отправьте свой номер кнопкой ниже.",
		"received": "✅ Номер телефона сохранён.",
	},
	"uz": {
		"prompt": "📱 Telefon raqamingizni yuborish va davom etish uchun quyidagi tugmani bosing.",
		"retry": "📱 Iltimos, o'z raqamingizni pastdagi tugma orqali yuboring.",
		"received": "✅ Telefon raqamingiz saqlandi.",
	},
	"uz_cyr": {
		"prompt": "📱 Телефон рақамингизни юбориш ва давом этиш учун қуйидаги тугмани босинг.",
		"retry": "📱 Илтимос, ўз рақамингизни қуйидаги тугма орқали юборинг.",
		"received": "✅ Телефон рақамингиз сақланди.",
	},
}

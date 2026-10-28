"""Тексты запроса и сохранения номера телефона пользователя."""

from __future__ import annotations

PHONE_PROMPTS = {
	"ru": {
		"prompt": "📱 Отправьте свой номер телефона кнопкой ниже. Он нужен, чтобы поддержка могла с вами связаться.",
		"retry": "📱 Пожалуйста, отправьте свой номер кнопкой ниже.",
		"received": "✅ Номер телефона сохранён.",
	},
	"uz": {
		"prompt": "📱 Telefon raqamingizni quyidagi tugma orqali yuboring. U qo'llab-quvvatlash xizmati siz bilan bog'lanishi uchun kerak.",
		"retry": "📱 Iltimos, o'z raqamingizni pastdagi tugma orqali yuboring.",
		"received": "✅ Telefon raqamingiz saqlandi.",
	},
	"uz_cyr": {
		"prompt": "📱 Телефон рақамингизни қуйидаги тугма орқали юборинг. У қўллаб-қувватлаш хизмати сиз билан боғланиши учун керак.",
		"retry": "📱 Илтимос, ўз рақамингизни қуйидаги тугма орқали юборинг.",
		"received": "✅ Телефон рақамингиз сақланди.",
	},
}

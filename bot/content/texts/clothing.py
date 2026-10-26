"""Тексты раздела «Одежда»: выбор региона и продавца."""

from __future__ import annotations

# Подпись кнопки «Одежда».
CLOTHING_BUTTONS = {
	"ru": "👕 Одежда",
	"uz": "👕 Kiyimlar",
	"uz_cyr": "👕 Кийимлар",
}

# Текст выбора региона.
CLOTHING_REGION_PROMPTS = {
	"ru": "📍 Выберите свой регион:",
	"uz": "📍 O'z viloyatingizni tanlang:",
	"uz_cyr": "📍 Ўз вилоятингизни танланг:",
}

# Текст выбора продавца после выбора региона.
CLOTHING_SELLER_PROMPTS = {
	"ru": "🛍 Регион: {region}\nВыберите продавца:",
	"uz": "🛍 Viloyat: {region}\nSotuvchini tanlang:",
	"uz_cyr": "🛍 Вилоят: {region}\nСотувчини танланг:",
}

# Продавец одежды.
CLOTHING_SELLER_BUTTONS = {
	"ru": "🛍 Акрам",
	"uz": "🛍 Akram",
	"uz_cyr": "🛍 Акрам",
}

CLOTHING_REGION_NOT_FOUND_TEXTS = {
	"ru": "Регион не найден. Нажмите кнопку «Одежда» и выберите регион снова.",
	"uz": "Viloyat topilmadi. «Kiyimlar» tugmasini bosib, viloyatni qayta tanlang.",
	"uz_cyr": "Вилоят топилмади. «Кийимлар» тугмасини босиб, вилоятни қайта танланг.",
}

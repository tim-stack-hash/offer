"""Тексты, связанные с выбором и сменой языка интерфейса, и приветственный экран."""

from __future__ import annotations

# Кнопки выбора языка на экране старта: (подпись, код языка).
LANGUAGE_BUTTONS = (
	("🇺🇿 O'zbekcha", "uz"),
	("🇷🇺 Русский", "ru"),
	("🇺🇿 Ўзбекча", "uz_cyr"),
)

# Подпись кнопки «Поменять язык» для каждого языка.
CHANGE_LANGUAGE_BUTTONS = {
	"ru": "🌐 Поменять язык",
	"uz": "🌐 Tilni o'zgartirish",
	"uz_cyr": "🌐 Тилни ўзгартириш",
}

# Подпись кнопки отправки номера телефона.
CONTACT_BUTTON_TEXT = {
	"ru": "Отправить номер телефона",
	"uz": "Telefon raqamni yuborish",
	"uz_cyr": "Телефон рақамини юбориш",
}

SUBSCRIPTION_PROMPTS = {
	"ru": "Чтобы продолжить пользоваться ботом, вступите в группу\n"
        "SMART DUNYO.",
	"uz": "Botdan foydalanishni davom ettirish uchun guruhimizga qo‘shiling va «Qo‘shildim» tugmasни bosing.",
	"uz_cyr": "Ботдан фойдаланишни давом эттириш учун гуруҳимизга қўшилинг ва «Қўшилдим» тугмасни босинг.",
}

SUBSCRIPTION_BUTTONS = {
	"ru": ("📢 Вступить в группу", "✅ Я вступил(а)"),
	"uz": ("📢 Guruhga qo‘shilish", "✅ Qo‘shildim"),
	"uz_cyr": ("📢 Гуруҳга қўшилиш", "✅ Қўшилдим"),  
}

SUBSCRIPTION_WELCOME_TEXTS = {
	"ru": "✅ Вы вступили в группу. Добро пожаловать в бот SMART DUNYO!",
	"uz": "✅ Guruhga qo‘shildingiz. SMART DUNYO botiga xush kelibsiz!",
	"uz_cyr": "✅ Гуруҳга қўшилдингиз. SMART DUNYO ботига хуш келибсиз!",
}

# Кнопка обращения в поддержку.
SUPPORT_BUTTON_TEXT = {
	"ru": "🆘 Поддержка",
	"uz": "🆘 Yordam",
	"uz_cyr": "🆘 Ёрдам",
}

FEEDBACK_BUTTON_TEXT = {
	"ru": "💡 Предложения и жалобы",
	"uz": "💡 Taklif va shikoyatlar",
	"uz_cyr": "💡 Таклиф ва шикоятлар",
}

FEEDBACK_CATEGORY_BUTTONS = {
	"ru": ("💡 Предложение", "⚠️ Жалоба"),
	"uz": ("💡 Taklif", "⚠️ Shikoyat"),
	"uz_cyr": ("💡 Таклиф", "⚠️ Шикоят"),
}

FEEDBACK_CATEGORY_PROMPTS = {
	"ru": "Выберите, что хотите отправить:",
	"uz": "Nima yubormoqchi ekaningizni tanlang:",
	"uz_cyr": "Нима юбормоқчи эканингизни танланг:",
}

FEEDBACK_MESSAGE_PROMPTS = {
	"ru": {
		"proposal": "Напишите ваше предложение одним сообщением.",
		"complaint": "Опишите жалобу одним сообщением.",
	},
	"uz": {
		"proposal": "Taklifingizni bitta xabarda yozing.",
		"complaint": "Shikoyatingizni bitta xabarda yozing.",
	},
	"uz_cyr": {
		"proposal": "Таклифингизни битта хабарда ёзинг.",
		"complaint": "Шикоятингизни битта хабарда ёзинг.",
	},
}

FEEDBACK_SUCCESS_TEXTS = {
	"ru": "✅ Спасибо! Ваше сообщение отправлено.",
	"uz": "✅ Rahmat! Xabaringiz yuborildi.",
	"uz_cyr": "✅ Раҳмат! Хабарингиз юборилди.",
}

FEEDBACK_CANCELLED_TEXTS = {
	"ru": "Отправка сообщения отменена.",
	"uz": "Xabar yuborish bekor qilindi.",
	"uz_cyr": "Хабар юбориш бекор қилинди.",
}

FEEDBACK_TOO_LONG_TEXTS = {
	"ru": "Сообщение слишком длинное. Отправьте текст короче.",
	"uz": "Xabar juda uzun. Qisqaroq matn yuboring.",
	"uz_cyr": "Хабар жуда узун. Қисқароқ матн юборинг.",
}

SUPPORT_PROMPTS = {
	"ru": """Здраствуйте! Столкнулись со сложностями? Давайте исправим.
• Напишите всё одним сообщением в этот чат — оператор уже подключается.
• Или позвоните нам в один клик: [+998712009333], если вам удобнее объяснить голосом.""",

	"uz": """Xizmat ko‘rsatishda qiyinchiliklarga duch keldingizmi? Keling, buni tuzatamiz.
• Barchasini ushbu chatga bitta xabar qilib yozing — operator hozir ulanadi.
• Yoki agar ovozli tushuntirish qulayroq bo‘lsa, birgina bosish bilan bizga qo‘ng‘iroq qiling: [+998712009333].""",

	"uz_cyr": """Хизмат кўрсатишда қийинчиликларга дуч келдингизми? Келинг, буни тузатамиз.
• Барчасини ушбу чатга битта хабар қилиб ёзинг — оператор ҳозир уланади.
• Ёки агар овозли тушунтириш қулайроқ бўлса, биргина босиш билан бизга қўнғироқ қилинг: [+998712009333].""",
}

SUPPORT_CANCEL_BUTTONS = {
	"ru": "❌ Отмена",
	"uz": "❌ Bekor qilish",
	"uz_cyr": "❌ Бекор қилиш",
}

SUPPORT_CANCELLED_TEXTS = {
	"ru": "Отправка обращения отменена.",
	"uz": "Murojaat yuborish bekor qilindi.",
	"uz_cyr": "Мурожаат юбориш бекор қилинди.",
}

SUPPORT_SUCCESS_TEXTS = {
	"ru": "✅ Ожидайте ответ.",
	"uz": "✅ Javobni kuting.",
	"uz_cyr": "✅ Жавобни кутинг.",
}

SUPPORT_TOO_LONG_TEXTS = {
	"ru": "Сообщение слишком длинное. Пожалуйста, отправьте обращение короче.",
	"uz": "Xabar juda uzun. Iltimos, murojaatni qisqaroq yuboring.",
	"uz_cyr": "Хабар жуда узун. Илтимос, мурожаатни қисқароқ юборинг.",
}

# Приветственный текст на экране /start (запасной вариант, основной текст задан прямо в обработчике).
START_TEXTS = {
	"ru": "👋 Здравствуйте!\nЧерез эту платформу вы можете узнать о правилах колоний и разрешенных вещах для заключенных.\n\n🌐 Выберите язык:",
	"uz": "👋 Assalomu alaykum!\nUshbu platforma orqali koloniyalar tartibi va mahkumlar uchun ruxsat etilgan buyumlar haqida ma'lumot olishingiz mumkin.\n\n🌐 Tilni tanlang:",
	"uz_cyr": "👋 Ассалому алайкум!\nУшбу платформа орқали колониялар тартиби ва маҳкумлар учун рухсат этилган буюмлар ҳақида маълумот олишингиз мумкин.\n\n🌐 Тилни танланг:",
}

# Смена языка из меню и подтверждение выбора.
CHANGE_LANGUAGE_PROMPTS = {
	"ru": "🌐 Выберите новый язык:",
	"uz": "🌐 Yangi tilni tanlang:",
	"uz_cyr": "🌐 Янги тилни танланг:",
}

LANGUAGE_SELECTED_TEXTS = {
	"ru": "🇷🇺 Вы выбрали русский язык.",
	"uz": "🇺🇿 O'zbek tili tanlandi.",
	"uz_cyr": "🇺🇿 Ўзбек тили танланди.",
}

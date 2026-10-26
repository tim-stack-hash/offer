"""Список колоний, их координаты, ссылки на группы и данные гостиниц."""

from __future__ import annotations

# Координаты гостиницы и телефон гостиницы для каждой колонии: (координаты, телефон).
# Пустой кортеж/строка означает, что данные пока не добавлены.
HOTEL_INFO = {
	"SmartJIEK1": ((39.726978, 64.529781), "+998652207006"),  # 1-son koloniya
	"SmartJIEK2": ((38.902532, 65.792938), "+998902443706 "),  # 2-son koloniya
	"SmartJIEK3": ((38.902532, 65.792938), "+998902443706"),  # 3-son koloniya
	"SmartJIEK4": ((39.726978, 64.529781), "+998956076490"),  # 4-son koloniya
	"SmartJIEK5": ((40.029866, 64.831108), ""),  # 5-son koloniya
	"SmartJIEK6": ((40.923440, 71.052568), "+998999221366"),  # 6-son koloniya
	"SmartJIEK7": ((41.553110, 69.687068), "+998993136306"),  # 7-son koloniya
	"SmartJIEK10":((), ""),  # 10-son koloniya
	"SmartJIEK11":((), ""),  # 11-son koloniya
	"SmartJIEK12":((), ""),  # 12-son koloniya
	"SmartJIEK13":((), "+998943934159"),  # 13-son koloniya
	"SmartJIEK14":((), ""),  # 14-son koloniya
	"SmartJIEK17":((), "+998942490009"),  # 17-son koloniya
	"SmartJIEK20":((), ""),  # 20-son koloniya
	"SmartJIEK21":((), ""),  # 21-son koloniya
	"SmartJIEK22":((), ""),  # 22-son koloniya
	"SmartJIEK23":((), ""),  # 23-son koloniya
}

# Географические координаты (широта, долгота) каждой колонии.
COLONY_COORDINATES = {
	"SmartJIEK1":  (39.7033, 64.4867),
	"SmartJIEK2":  (38.9283, 65.7561),
	"SmartJIEK3":  (38.9256, 65.7611),
	"SmartJIEK4":  (40.115, 65.3506),
	"SmartJIEK5":  (40.0389, 64.8333),
	"SmartJIEK6":  (40.9294, 71.0458),
	"SmartJIEK7":  (41.5536, 69.6869),
	"SmartJIEK10": (39.0631, 65.5597),
	"SmartJIEK11": (40.0617, 65.2831),
	"SmartJIEK12": (41.5875, 64.1933),
	"SmartJIEK13": (41.4268, 69.594),
	"SmartJIEK14": (40.8583, 69.5044),
	"SmartJIEK17": (39.5131, 64.7839),
	"SmartJIEK20": (39.7192, 64.5647),
	"SmartJIEK21": (41.1797, 69.1614),
	"SmartJIEK22": (41.1789, 69.1672),
	"SmartJIEK23": (41.2482, 69.3284),
}

# Telegram-юзернейм группы каждой колонии.
COLONY_GROUP_LINKS = {
	"SmartJIEK1": "@SmartJIEK1", "SmartJIEK2": "@SmartJIEK2", "SmartJIEK3": "@SmartJIEK3",
	"SmartJIEK4": "@SmartJIEK4", "SmartJIEK5": "@SmartJIEK5", "SmartJIEK6": "@SmartJIEK6",
	"SmartJIEK7": "@SmartJIEK7", "SmartJIEK10":"@SmartJIEK10","SmartJIEK11":"@SmartJIEK11",              
	"SmartJIEK12":"@SmartJIEK12","SmartJIEK13":"@SmartJIEK13","SmartJIEK14":"@SmartJIEK14",
	"SmartJIEK17":"@SmartJIEK17","SmartJIEK20":"@SmartJIEK20","SmartJIEK21":"@SmartJIEK21",
	"SmartJIEK22":"@SmartJIEK22","SmartJIEK23":"@SmartJIEK23",
}

# Порядок колоний — индекс в этом кортеже используется в callback_data кнопок выбора.
COLONY_GROUPS = (
	"SmartJIEK1", "SmartJIEK2",  "SmartJIEK3",  "SmartJIEK4",  "SmartJIEK5",  "SmartJIEK6",
	"SmartJIEK7", "SmartJIEK10", "SmartJIEK11", "SmartJIEK12", "SmartJIEK13", "SmartJIEK14",
	"SmartJIEK17","SmartJIEK20", "SmartJIEK21", "SmartJIEK22", "SmartJIEK23",
)

# Подписи кнопок выбора колонии на каждом языке (порядок соответствует COLONY_GROUPS).
COLONY_GROUP_LABELS = {
	"ru": (
		"📍 1-я колония",  "📍 2-я колония",     "📍 3-я колония",
		"📍 4-я колония",  "📍 5-я колония",     "📍 6-я колония",
		"📍 7-я колония",  "📍 10-я колония",    "📍 11-я колония",
		"📍 12-я колония", "📍 13-я колония",    "📍 14-я колония",
		"📍 17-я колония", "📍 20-я колония",    "📍 21-я колония",
		"📍 22-я колония", "📍 23-я колония 🏥",
	),
	"uz": (
		"📍 1-son JIEK",   "📍 2-son JIEK", "  📍 3-son JIEK",
		"📍 4-son JIEK",   "📍 5-son JIEK", "  📍 6-son JIEK ",
		"📍 7-son JIEK",   "📍 10-son JIEK ", "📍 11-son JIEK",
		"📍 12-son JIEK ", "📍 13-son JIEK)", "📍 14-son JIEK",
		"📍 17-son JIEK ", "📍 20-son JIEK",  "📍 21-son JIEK ",
		"📍 22-son JIEK ", "📍 23-son MUIK) 🏥",
	),
	"uz_cyr": (
		"📍 1-сон ЖИЭК", "📍 2-сон ЖИЭК ", "📍 3-сон ЖИЭК ",
		"📍 4-сон ЖИЭК ", "📍 5-сон ЖИЭК ", "📍 6-сон ЖИЭК ",
		"📍 7-сон ЖИЭК ", "📍 10-сон ЖИЭК", "📍 11-сон ЖИЭК",
		"📍 12-сон ЖИЭК", "📍 13-сон ЖИЭК", "📍 14-сон ЖИЭК",
		"📍 17-сон ЖИЭК", "📍 20-сон ЖИЭК", "📍 21-сон ЖИЭК",
		"📍 22-сон ЖИЭК", "📍 23-сон МУИК 🏥",
	),
}

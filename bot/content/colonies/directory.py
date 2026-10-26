"""Текст справочника: общий заголовок Департамента и контакты конкретной колонии."""

from __future__ import annotations

from bot.content.colonies.directory_data import COLONY_DIRECTORY_EXTRA_CONTACTS

# Заголовок справочника (колл-центр и официальные контакты Департамента) на каждом языке.
COLONY_DIRECTORY_HEADERS = {
	"ru": (
        "Контакты МВД РУз:\n"   
		"Приемная: +998712314304\n"
		"Канцелярия: +998712913353\n"
		"Телефон доверия: 1102\n\n"
		"Kонтакты Департамента:\n"
		"Колл-центр: +998712072777"
	),
	"uz": (
		"O‘zR IIV aloqa raqamlari:\n"
		"Qabulxona: +998712314304\n"
		"Devonxona: +998712913353\n"
		"O'zbekiston ishonch telefoni: 1102\n\n"
		"Departament aloqa raqamlari:\n"
		"Koll-markazi: +998712072777\n"
	),
	"uz_cyr": (
		"УЗр ИИB алока :\n"
		"Кабулхона: +998712314304\n"
		"Девонхона: +998712913353\n"
		"Ўзбекистон ишонч телефони: 1102\n\n"
		"Департамент алока ракамлари:\n"
		"Колл-маркази: +998712072777\n"
	),
}

# Заголовок раздела контактов колонии в справочнике: (uz_cyr, uz, ru).
COLONY_DIRECTORY_CONTACTS = {
	"SmartJIEK1":   ("1-сон колония контактлари",  "1-son koloniya kontaktlari",  "Контакты 1-й колонии"),
	"SmartJIEK2":   ("2-сон колония контактлари",  "2-son koloniya kontaktlari",  "Контакты 2-й колонии"),
	"SmartJIEK3":   ("3-сон колония контактлари",  "3-son koloniya kontaktlari",  "Контакты 3-й колонии"),
	"SmartJIEK4":   ("4-сон колония контактлари",  "4-son koloniya kontaktlari",  "Контакты 4-й колонии"),
	"SmartJIEK5":   ("5-сон колония контактлари",  "5-son koloniya kontaktlari",  "Контакты 5-й колонии"),
	"SmartJIEK6":   ("6-сон колония контактлари",  "6-son koloniya kontaktlari",  "Контакты 6-й колонии"),
	"SmartJIEK7":   ("7-сон колония контактлари",  "7-son koloniya kontaktlari",  "Контакты 7-й колонии"),
	"SmartJIEK10": ("10-сон колония контактлари", "10-son koloniya kontaktlari",  "Контакты 10-й колонии"),
	"SmartJIEK11": ("11-сон колония контактлари", "11-son koloniya kontaktlari",  "Контакты 11-й колонии"),
	"SmartJIEK12": ("12-сон колония контактлари", "12-son koloniya kontaktlari",  "Контакты 12-й колонии"),
	"SmartJIEK13": ("13-сон колония контактлари", "13-son koloniya kontaktlari",  "Контакты 13-й колонии"),
	"SmartJIEK14": ("14-сон колония контактлари", "14-son koloniya kontaktlari",  "Контакты 14-й колонии"),
	"SmartJIEK17": ("17-сон колония контактлари", "17-son koloniya kontaktlari",  "Контакты 17-й колонии"),
	"SmartJIEK21": ("21-сон колония контактлари", "21-son koloniya kontaktlari",  "Контакты 21-й колонии"),
	"SmartJIEK22": ("22-сон колония контактлари", "22-son koloniya kontaktlari",  "Контакты 22-й колонии"),
	"SmartJIEK23":    ("23-сон МУИК контактлари",     "23-son MUIK kontaktlari",  "Контакты 23-го МУИК"),
}


def colony_directory_text(language: str, colony_group: str | None) -> str:
	"""Собирает текст справочника: общий заголовок Департамента плюс контакты конкретной колонии."""
	language_index = {"uz_cyr": 0, "uz": 1, "ru": 2}.get(language, 2)
	text = COLONY_DIRECTORY_HEADERS.get(language, COLONY_DIRECTORY_HEADERS["ru"])
	if colony_group is None:
		return text

	if colony_group in COLONY_DIRECTORY_CONTACTS:
		colony_title = COLONY_DIRECTORY_CONTACTS[colony_group][language_index]
		text += f"\n\n{colony_title}:"
		for contact in COLONY_DIRECTORY_EXTRA_CONTACTS.get(colony_group, ()):
			label = contact[language_index]
			values = ", ".join(contact[3:])
			text += f"\n{label}: {values}"
	call_center_labels = {
		"ru": "Кол-центр SMART DUNYO:",
		"uz": "SMART DUNYO PAY kol-center:",
		"uz_cyr": "SMART DUNYO PAY кол-центр:",
	}
	text += f"\n\n{call_center_labels.get(language, call_center_labels['ru'])} +998712009333"
	return text

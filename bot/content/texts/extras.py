"""Тексты дополнительных кнопок меню колонии: гостиница, разделы в разработке, заявления."""

from __future__ import annotations

# Подписи дополнительных кнопок меню колонии: гостиница, магазин, такси,
# адвокаты, перевод денег, дополнительная информация и портал my.gov.uz.
ADDITIONAL_INFO_BUTTONS = {
	"ru": (
		"🏨 Гостиница",
		"🛍 Магазин",
		"🚕 Такси",
		"⚖️ Адвокаты",
		"💸 Перевести деньги",
		"ℹ️ Доп. информация",
		"🌐 My.gov",
	),
	"uz": (
		"🏨 Mehmonxona",
		"🛍 Do'kon",
		"🚕 Taksi",
		"⚖️ Advokatlar",
		"💸 Pul o'tkazish",
		"ℹ️ Qo'shimcha ma'lumot",
		"🌐 my.gov",
	),
	"uz_cyr": (
		"🏨 Меҳмонхона",
		"🛍 Дўкон",
		"🚕 Такси",
		"⚖️ Адвокатлар",
		"💸 Пул ўтказиш",
		"ℹ️ Қўшимча маълумот",
		"🌐 my.gov",
	),
}    

ADDITIONAL_INFO_LIST_TEXTS = {
	"ru": """СПИСОК ПРОДУКТОВ

1. Жареное мясо
2. Қазы — 2 палки, в вакуумной упаковке
3. Индейка — 1 палка
4. Охотничьи сосиски — 1 кг
5. M&M’s, чёрный шоколад — 1 кг
6. Конфеты — 0,5 или 1 кг
7. Қурт — 0,5 или 1 кг
8. Казахский шоколад — 4 плитки
9. Сырные палочки — 4 пачки
10. Наввот — 0,5 или 1 кг
11. Чёрный чай
12. Фруктовый чай
13. Зелёный чай с лимоном — 2 или 4 шт.
14. Сигареты Parliament Aqua Blue — 4 блока
15. Зажигалки — 6 шт.
16. Контик — 6 пачек
17. Натуральный мёд
18. Микс орехов: грецкий орех, фисташки, миндаль, изюм, арахис
19. Сушёная хурма и финики
20. Курага без косточек
21. Чеснок
22. Приправа «Универсальная»
23. Чёрный кофе
24. Сливочное масло
25. Шоколадная паста Chococrem
26. Сгущённое молоко
27. Сухие сливки / сухое молоко
28. Печенье
29. Вафли
30. Пряники
31. Сушки
32. Брауни
33. Шоколад «Казахский» — 2–4 плитки
34. Батончики Roshen — 6–10 шт.
35. Snickers — 1 кг
36. Bounty — 1 кг
37. Мини-рулеты — 12 шт.
38. Русский бисквит — 12 шт.
39. Большие патыр-лепёшки — 4 шт.

СПИСОК ВЕЩЕЙ

40. Робa (верх и низ) — 2 комплекта
41. Обувь Salamander / Cheetos с жёлтой гелевой подошвой
42. Стельки для обуви — 2 пары, чёрные сетчатые
43. Белое постельное бельё
44. Гостевой комплект постельного белья
45. Набор полотенец — 3 шт.
46. Большая тёмная сумка для покупок
47. Маленькая сумка для душевых принадлежностей
48. Чёрные майки и шорты — по 2 шт. каждого вида, при возможности по 4 шт.
49. Хлопчатобумажные носки — 6 пар
50. Кепки-чепчики — 2 шт.
51. Нижнее бельё и кальсоны
52. Чёрные носовые платки — 6 шт.
53. Машинка для стрижки волос и бороды
54. Шампунь
55. Антиперспирант
56. Душистое туалетное мыло — 2 шт.
57. Белое хозяйственное мыло — 2 шт.
58. Мочалка
59. Жидкий гель для стирки — 3 или 5 литров
60. Пластмассовая миска, кружка и ложка
61. Крем для рук от сухости и трещин
62. Чёрный крем для обуви — 2 шт.
63. Щётка для обуви
64. Ролик для удаления пыли и ворса
65. Зубная паста Blend-a-med
66. Зубные щётки — 2 шт.
67. Мисвак
68. Мыльница
69. Резиновые тапочки для душа
70. Салфетки в рулоне для рук
71. Бумага — 1 блок
72. Спички — 5–10 пачек
73. Средство от потливости ног: Тимурова паста или Dry Dry.""",
	"uz": """MAHSULOTLAR RO‘YXATI

1. Qovurilgan go‘sht
2. Qazi — 2 ta tayoqcha, vakuum qadoqda
3. Indeyka — 1 ta tayoqcha
4. Oxotnichiy sosiska — 1 kg
5. M&M’s qora shokoladi — 1 kg
6. Konfet — 0,5 yoki 1 kg
7. Qurt — 0,5 yoki 1 kg
8. Qozoq shokoladi — 4 ta plitka
9. Sirli tayoqchalar — 4 pachka
10. Novvot — 0,5 yoki 1 kg
11. Toza qora choy
12. Mevali choy
13. Limonli ko‘k choy — 2 yoki 4 ta
14. Parliament Aqua Blue sigaretasi — 4 blok
15. Zajigalka — 6 ta
16. Kontik — 6 pachka
17. Toza asal
18. Yong‘oqlar miksi: gretskiy yong‘oq, xandon pista, bodom, mayiz va yeryong‘oq
19. Quritilgan xurmo va finik
20. Danagi olingan turshak
21. Sarimsoq
22. Universalniy priyprava
23. Qora kofe
24. Sariyog‘
25. Chococrem shokolad pastasi
26. Sgushyonka
27. Quruq slivki / quruq sut
28. Pechenye
29. Vafli
30. Pryanik
31. Sushka
32. Brauni shirinligi
33. Qozoq shokoladi — 2–4 ta plitka
34. Roshen batonchiklari — 6–10 ta
35. Snickers — 1 kg
36. Bounty — 1 kg
37. Mini-rulet — 12 ta
38. Russkiy biskvit — 12 ta
39. Katta patir non — 4 ta

KIYIM-KECHAK VA BOSHQA BUYUMLAR

40. Roba (tepasi-pasti) — 2 komplekt
41. Salamander / Cheetos oyoq kiyimi, tagi sariq gelli
42. Oyoq kiyim uchun qora setkali stelka — 2 juft
43. Oq postel
44. Gostinniy postel komplekti
45. Sochiqlar nabori — 3 talik
46. Katta, to‘q rangli bozor sumkasi
47. Hammom buyumlari uchun kichkina sumka
48. Qora mayka va shortik — har biridan 2 tadan, imkon bo‘lsa 4 tadan
49. Xlopok noski — 6 juft
50. Kepka-chepchik — 2 ta
51. Belyo va kalson
52. Qora dastro‘molcha — 6 ta
53. Soch va soqol oladigan mashinka
54. Shampun
55. Antiperspirant
56. Atir sovun — 2 ta
57. Oq kir sovun — 2 ta
58. Mochalka
59. Kir yuvish uchun suyuq gel — 3 yoki 5 litrlik
60. Plastmassa tovoq, krujka va qoshiq
61. Qo‘l qurishi va yorilishiga qarshi krem
62. Oyoq kiyim uchun qora moy — 2 ta
63. Oyoq kiyim cho‘tkasi
64. Chang va tuklarni oladigan rolik
65. Blend-a-med tish pastasi
66. Tish cho‘tkasi — 2 ta
67. Misvok
68. Sovun idish
69. Hammom uchun rezinali tapochka
70. Qo‘l uchun rulonli salfetka
71. Qog‘oz — 1 blok
72. Gugurt — 5–10 pachka
73. Oyoq terlashiga qarshi vosita: Timurov pastasi yoki Dry Dry.""",
	"uz_cyr": """МАҲСУЛОТЛАР РЎЙХАТИ

1. Қовурилган гўшт
2. Қази — 2 та таёқча, вакуум қадоқда
3. Индейка — 1 та таёқча
4. Овчилик сосискалари — 1 кг
5. M&M’s қора шоколади — 1 кг
6. Конфет — 0,5 ёки 1 кг
7. Қурт — 0,5 ёки 1 кг
8. Қозоқ шоколади — 4 та плитка
9. Сырли таёқчалар — 4 пачка
10. Наввот — 0,5 ёки 1 кг
11. Тоза қора чой
12. Мевали чой
13. Лимонли кўк чой — 2 ёки 4 та
14. Parliament Aqua Blue сигаретаси — 4 блок
15. Зажигалка — 6 та
16. Контик — 6 пачка
17. Табиий асал
18. Ёнғоқлар микси: грецкий ёнғоқ, хандон писта, бодом, майиз ва ерёнғоқ
19. Қуритилган хурмо ва финик
20. Данаги олинган туршак
21. Саримсоқ
22. «Универсал» приправа
23. Қора кофе
24. Сариёғ
25. Chococrem шоколад пастаси
26. Сгущёнка
27. Қуруқ сливки / қуруқ сут
28. Печенье
29. Вафли
30. Пряник
31. Сушка
32. Брауни ширинлиги
33. Қозоқ шоколади — 2–4 та плитка
34. Roshen батончиклари — 6–10 та
35. Snickers — 1 кг
36. Bounty — 1 кг
37. Мини-рулет — 12 та
38. Русский бисквит — 12 та
39. Катта патир нон — 4 та

КИЙИМ-КЕЧАК ВА БОШҚА БУЮМЛАР

40. Робa (тепа-паси) — 2 комплект
41. Salamander / Cheetos оёқ кийими, таги сариқ гелли
42. Оёқ кийим учун қора сеткали стелька — 2 жуфт
43. Оқ постель
44. Меҳмонхона учун постель комплекти
45. Сочиқлар набори — 3 талик
46. Катта, тўқ рангли бозор сумкаси
47. Ҳаммом буюмлари учун кичик сумка
48. Қора майка ва шортик — ҳар биридан 2 тадан, имкони бўлса 4 тадан
49. Хлопок наски — 6 жуфт
50. Кепка-чепчик — 2 та
51. Бельё ва кальсон
52. Қора даструмолча — 6 та
53. Соч ва соқол оладиган машинка
54. Шампунь
55. Антиперспирант
56. Атир совун — 2 та
57. Оқ кир совун — 2 та
58. Мочалка
59. Кир ювиш учун суюқ гель — 3 ёки 5 литрлик
60. Пластмасса товоқ, кружка ва қошиқ
61. Қўл қуриши ва ёрилишига қарши крем
62. Оёқ кийим учун қора мой — 2 та
63. Оёқ кийим чўткаси
64. Чанг ва тукларни оладиган ролик
65. Blend-a-med тиш пастаси
66. Тиш чўткаси — 2 та
67. Мисвок
68. Совун идиш
69. Ҳаммом учун резинали тапочка
70. Қўл учун рулонли салфетка
71. Қоғоз — 1 блок
72. Гугурт — 5–10 пачка
73. Оёқ терлашига қарши восита: Тимуров пастаси ёки Dry Dry.""",
}

TRANSFER_MONEY_PROMPTS = {
	"ru": "Выберите удобное приложение для перевода:",
	"uz": "Pul o'tkazish uchun o'zingizga qulay ilovani tanlang:",
	"uz_cyr": "Пул ўтказиш учун ўзингизга қулай иловани танланг:",
}

MONEY_TRANSFER_PROMPT_TEXTS = {
	"ru": "Хотите узнать, как отправить деньги близкому человеку? Нажмите «Да», и я пришлю инструкции.",
	"uz": "Yaqin insoningizga pul yuborishni bilmoqchimisiz? «Ha» tugmasini bosing, yo'riqnomalarni yuboraman.",
	"uz_cyr": "Яқин инсонингизга пул юборишни билмоқчимисиз? «Ҳа» тугмасини босинг, йўриқномаларни юбораман.",
}
MONEY_TRANSFER_SENDING_TEXTS = {
	"ru": "Отправляю изображение и видео по очереди. Первая загрузка может занять время.",
	"uz": "Rasm va videolarni navbat bilan yuboryapman. Birinchi yuklash biroz vaqt olishi mumkin.",
	"uz_cyr": "Расм ва видеоларни навбат билан юборяпман. Биринчи юклаш бироз вақт олиши мумкин.",
}
MONEY_TRANSFER_YES_BUTTONS = {
	"ru": "Да",
	"uz": "Ha",
	"uz_cyr": "Ҳа",
}
MONEY_TRANSFER_NO_BUTTONS = {
	"ru": "Нет",
	"uz": "Yo'q",
	"uz_cyr": "Йўқ",
}

# Тексты выбора региона и адвоката.
LAWYER_REGION_PROMPTS = {
	"ru": "📍 Выберите свой регион:",
	"uz": "📍 O'z viloyatingizni tanlang:",
	"uz_cyr": "📍 Ўз вилоятингизни танланг:",
}

LAWYER_REGION_NOT_FOUND_TEXTS = {
	"ru": "Регион не найден. Нажмите кнопку «Адвокаты» и выберите регион снова.",
	"uz": "Viloyat topilmadi. «Advokatlar» tugmasini bosib, viloyatni qayta tanlang.",
	"uz_cyr": "Вилоят топилмади. «Адвокатлар» тугмасини босиб, вилоятни қайта танланг.",
}

LAWYER_PROMPTS = {
	"ru": "⚖️ Регион: {region}\nВыберите адвоката:",
	"uz": "⚖️ Viloyat: {region}\nAdvokatni tanlang:",
	"uz_cyr": "⚖️ Вилоят: {region}\nАдвокатни танланг:",
}

LAWYER_LIST_EMPTY_TEXTS = {
	"ru": "В этом регионе пока нет адвокатов.",
	"uz": "Bu hududda hozircha advokatlar yo'q.",
	"uz_cyr": "Бу ҳудудда ҳозирча адвокатлар йўқ.",
}

LAWYER_PROFILE_CAPTIONS = {
	"ru": "⚖️ Адвокат: {name}\n📍 Регион: {region}\n⭐ Отзывов: {review_count}",
	"uz": "⚖️ Advokat: {name}\n📍 Hudud: {region}\n⭐ Sharhlar: {review_count}",
	"uz_cyr": "⚖️ Адвокат: {name}\n📍 Ҳудуд: {region}\n⭐ Фикрлар: {review_count}",
}

LAWYER_ACTION_BUTTONS = {
	"ru": ("⭐ Отзывы", "📞 Связаться"),
	"uz": ("⭐ Sharhlar", "📞 Bog'lanish"),
	"uz_cyr": ("⭐ Фикрлар", "📞 Боғланиш"),
}

LAWYER_CALL_PROMPTS = {
	"ru": "Нажмите на номер, чтобы позвонить:",
	"uz": "Qo'ng'iroq qilish uchun raqamni bosing:",
	"uz_cyr": "Қўнғироқ қилиш учун рақамни босинг:",
}

LAWYER_REVIEW_MENU_PROMPTS = {
	"ru": "Что хотите сделать с отзывами об адвокате?",
	"uz": "Advokat haqidagi sharhlar bo'yicha nima qilmoqchisiz?",
	"uz_cyr": "Адвокат ҳақидаги фикрлар бўйича нима қилмоқчисиз?",
}

LAWYER_REVIEW_MENU_BUTTONS = {
	"ru": ("✍️ Оставить отзыв", "📖 Посмотреть отзывы"),
	"uz": ("✍️ Sharh qoldirish", "📖 Sharhlarni ko'rish"),
	"uz_cyr": ("✍️ Фикр қолдириш", "📖 Фикрларни кўриш"),
}

LAWYER_REVIEW_PROMPTS = {
	"ru": "Напишите отзыв о работе адвоката {name}.",
	"uz": "{name} advokatning ishi haqida sharh yozing.",
	"uz_cyr": "{name} адвокатнинг иши ҳақида фикр ёзинг.",
}

LAWYER_REVIEW_SUCCESS_TEXTS = {
	"ru": "Спасибо! Ваш отзыв опубликован.",
	"uz": "Rahmat! Sharhingiz e'lon qilindi.",
	"uz_cyr": "Раҳмат! Фикрингиз эълон қилинди.",
}

LAWYER_REVIEW_PUBLISH_ERROR_TEXTS = {
	"ru": "Отзыв сохранён, но не удалось опубликовать его в канале. Попробуйте позже или сообщите администратору.",
	"uz": "Sharh saqlandi, lekin kanalga joylab bo'lmadi. Keyinroq urinib ko'ring yoki administratorga xabar bering.",
	"uz_cyr": "Фикр сақланди, лекин каналга жойлаб бўлмади. Кейинроқ уриниб кўринг ёки администраторга хабар беринг.",
}

LAWYER_REVIEW_READ_ERROR_TEXTS = {
	"ru": "Не удалось загрузить отзывы. Попробуйте ещё раз позже.",
	"uz": "Sharhlarni yuklab bo'lmadi. Keyinroq qayta urinib ko'ring.",
	"uz_cyr": "Фикрларни юклаб бўлмади. Кейинроқ қайта уриниб кўринг.",
}

LAWYER_REVIEW_SAVE_ERROR_TEXTS = {
	"ru": "Не удалось сохранить отзыв. Попробуйте отправить его ещё раз позже.",
	"uz": "Sharhni saqlab bo'lmadi. Keyinroq qayta yuborib ko'ring.",
	"uz_cyr": "Фикрни сақлаб бўлмади. Кейинроқ қайта юбориб кўринг.",
}

LAWYER_REVIEW_EMPTY_TEXTS = {
	"ru": "Пока отзывов нет. Вы можете оставить первый.",
	"uz": "Hozircha sharhlar yo'q. Birinchi bo'lib sharh qoldirishingiz mumkin.",
	"uz_cyr": "Ҳозирча фикрлар йўқ. Биринчи бўлиб фикр қолдиришингиз мумкин.",
}

LAWYER_REVIEW_LIST_HEADERS = {
	"ru": "⭐ Отзывы об адвокате {name}:",
	"uz": "⭐ {name} advokat haqidagi sharhlar:",
	"uz_cyr": "⭐ {name} адвокат ҳақидаги фикрлар:",
}

LAWYER_REVIEW_AUTHOR_LABELS = {
	"ru": "Автор",
	"uz": "Muallif",
	"uz_cyr": "Муаллиф",
}

LAWYER_REVIEW_TOO_LONG_TEXTS = {
	"ru": "Отзыв слишком длинный. Отправьте текст не длиннее 3000 символов.",
	"uz": "Sharh juda uzun. 3000 belgidan oshmagan matn yuboring.",
	"uz_cyr": "Фикр жуда узун. 3000 белгидан ошмаган матн юборинг.",
}

# Текст на случай, если для колонии не заданы координаты/телефон гостиницы.
HOTEL_INFO_MISSING_TEXTS = {
	"ru": "Для этой колонии координаты гостиницы и телефон пока не добавлены.",
	"uz": "Bu koloniya uchun mehmonxona koordinatalari va telefoni hali qo'shilmagan.",
	"uz_cyr": "Бу колония учун меҳмонхона координаталари ва телефони ҳали қўшилмаган.",
}

# Подписи для локации и телефона гостиницы: (локация отправлена, телефон).
HOTEL_INFO_LABELS = {
	"ru": ("🏨 Локация гостиницы.", "📞 Телефон гостиницы:"),
	"uz": ("🏨 Mehmonxona lokatsiyasi yuqorida yuborildi.", "📞 Mehmonxona telefoni:"),
	"uz_cyr": ("🏨 Меҳмонхона локацияси юқорида юборилди.", "📞 Меҳмонхона телефони:"),
}

# Текст-заглушка для разделов, которые ещё не реализованы.
IN_DEVELOPMENT_TEXTS = {
	"ru": "🚧 Этот раздел пока в разработке. Информация появится позже.",
	"uz": "🚧 Ushbu bo'lim hozir ishlab chiqilmoqda. Ma'lumot keyinroq qo'shiladi.",
	"uz_cyr": "🚧 Ушбу бўлим ҳозир ишлаб чиқилмоқда. Маълумот кейинроқ қўшилади.",
}

# Текст на случай отсутствия файла-образца заявления на диске.
APPLICATION_FILE_MISSING_TEXTS = {
	"ru": "Файл образца заявления не найден.",
	"uz": "Ariza namunasi fayli topilmadi.",
	"uz_cyr": "Ариза намунаси файли топилмади.",
}

ADDITIONAL_INFO_COLONY_NUMBERS_TEXTS = {
	"ru": """Номера колоний:
Общий режим: № 1, 2, 3, 4, 5, 6, 7, 21, 22, 23.
Строгий режим: № 10, 11, 12, 13, 14, 17, 20.""",
	"uz": """Koloniyalar raqamlari:
Umumiy tartib: № 1, 2, 3, 4, 5, 6, 7, 21, 22, 23.
Qattiq tartib: № 10, 11, 12, 13, 14, 17, 20.""",
	"uz_cyr": """Колониялар рақамлари:
Умумий тартиб: № 1, 2, 3, 4, 5, 6, 7, 21, 22, 23.
Қаттиқ тартиб: № 10, 11, 12, 13, 14, 17, 20.""",
}

ADDITIONAL_INFO_IMAGE_MISSING_TEXTS = {
	"ru": "Не удалось найти изображения с дополнительной информацией.",
	"uz": "Qo'shimcha ma'lumot rasmlarini topib bo'lmadi.",
	"uz_cyr": "Қўшимча маълумот расмларини топиб бўлмади.",
}

# Инструкции по переводу денег отправлены полностью.
MONEY_TRANSFER_DONE_TEXTS = {
	"ru": "✅ Готово, все материалы отправлены.",
	"uz": "✅ Tayyor, barcha materiallar yuborildi.",
	"uz_cyr": "✅ Тайёр, барча материаллар юборилди.",
}

LAWYER_NOT_FOUND_TEXTS = {
	"ru": "Адвокат не найден. Откройте раздел «Адвокаты» заново.",
	"uz": "Advokat topilmadi. «Advokatlar» bo'limini qaytadan oching.",
	"uz_cyr": "Адвокат топилмади. «Адвокатлар» бўлимини қайтадан очинг.",
}

LAWYER_PHOTO_MISSING_TEXTS = {
	"ru": "Фото адвоката временно недоступно.",
	"uz": "Advokat surati vaqtincha mavjud emas.",
	"uz_cyr": "Адвокат сурати вақтинча мавжуд эмас.",
}

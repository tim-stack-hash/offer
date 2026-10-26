"""Публичный интерфейс пакета: все клавиатуры бота из тематических модулей."""

from __future__ import annotations

from bot.keyboards.colony import (
	MENU_SECTION_BUTTONS,
	application_type_keyboard,
	colony_group_keyboard,
	colony_group_link_keyboard,
	colony_location_keyboard,
	colony_location_reply_keyboard,
)
from bot.keyboards.common import (
	admin_activity_keyboard,
	admin_panel_keyboard,
	main_group_link_keyboard,
	money_transfer_apps_keyboard,
	money_transfer_confirmation_keyboard,
)
from bot.keyboards.clothing import clothing_regions_keyboard, clothing_sellers_keyboard
from bot.keyboards.language import (
	change_language_keyboard,
	contact_request_keyboard,
	feedback_category_keyboard,
	language_selection_keyboard,
	support_cancel_keyboard,
)
from bot.keyboards.lawyer import (
	lawyer_profile_keyboard,
	lawyer_review_menu_keyboard,
	lawyer_regions_keyboard,
	lawyers_by_region_keyboard,
)

__all__ = [
	"admin_activity_keyboard",
	"admin_panel_keyboard",
	"application_type_keyboard",
	"change_language_keyboard",
	"clothing_regions_keyboard",
	"clothing_sellers_keyboard",
	"colony_group_keyboard",
	"colony_group_link_keyboard",
	"colony_location_keyboard",
	"colony_location_reply_keyboard",
	"contact_request_keyboard",
	"feedback_category_keyboard",
	"language_selection_keyboard",
	"lawyer_profile_keyboard",
	"lawyer_review_menu_keyboard",
	"lawyer_regions_keyboard",
	"lawyers_by_region_keyboard",
	"main_group_link_keyboard",
	"MENU_SECTION_BUTTONS",
	"money_transfer_apps_keyboard",
	"money_transfer_confirmation_keyboard",
	"support_cancel_keyboard",
]

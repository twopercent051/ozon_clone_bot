from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class AdminInlineKeyboard:

    def __init__(self):
        pass

    @staticmethod
    def main_menu_kb():
        keyboard = [[InlineKeyboardButton(text="👩‍👦‍👦 Клонировать товары", callback_data="clone")]]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    def home_kb(self):
        keyboard = [self.home_button()]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def home_button():
        return [InlineKeyboardButton(text="🏡 На главную", callback_data="home")]

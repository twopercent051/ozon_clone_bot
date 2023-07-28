import os

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram import F, Router

from create_bot import bot, config
from .filters import AdminFilter
from .inline import AdminInlineKeyboard
from tgbot.misc.states import AdminFSM
from ...services.excel import xlsx_parser
from ...services.orecht import get_card_info
from ...services.ozon import OzonAPI

router = Router()
router.message.filter(AdminFilter())

inline = AdminInlineKeyboard()

ozon_api = OzonAPI()

admin_group = config.tg_bot.admin_group


async def main_screen_render(start: bool):
    if start:
        text = "Это главный экран бота. Чтобы скопировать карточки товаров, нажмите на клавишу нижу 👇"
    else:
        text = "ГЛАВНОЕ МЕНЮ"
    kb = inline.main_menu_kb()
    await bot.send_message(chat_id=admin_group, text=text, reply_markup=kb)


@router.message(Command("start"))
async def main_block(message: Message, state: FSMContext):
    await state.set_state(AdminFSM.home)
    await main_screen_render(start=True)


@router.callback_query(F.data == "home")
async def main_block(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminFSM.home)
    await main_screen_render(start=False)
    await bot.answer_callback_query(callback.id)


# @router.callback_query(F.data == "clone")
# async def main_block(callback: CallbackQuery, state: FSMContext):
#     file_name = f'{os.getcwd()}/template.xlsx'
#     file = FSInputFile(path=file_name, filename=file_name)
#     text = "Заполните шаблон ссылками и загрузите в бот"
#     kb = inline.home_kb()
#     await state.set_state(AdminFSM.get_data)
#     await callback.message.answer_document(document=file, caption=text, reply_markup=kb)
#     await bot.answer_callback_query(callback.id)


@router.callback_query(F.data == "clone")
async def main_block(callback: CallbackQuery, state: FSMContext):
    text = "Введите ClientID аккаунта"
    kb = inline.home_kb()
    await state.set_state(AdminFSM.client_id)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


@router.message(F.text, AdminFSM.client_id)
async def main_block(message: Message, state: FSMContext):
    text = "Введите токен"
    kb = inline.home_kb()
    await state.update_data(client_id=message.text.strip())
    await state.set_state(AdminFSM.api_token)
    await message.answer(text, reply_markup=kb)


@router.message(F.text, AdminFSM.api_token)
async def main_block(message: Message, state: FSMContext):
    file_name = f'{os.getcwd()}/template.xlsx'
    file = FSInputFile(path=file_name, filename=file_name)
    text = "Заполните шаблон ссылками и загрузите в бот"
    kb = inline.home_kb()
    await state.update_data(ozon_token=message.text.strip())
    await state.set_state(AdminFSM.get_data)
    await message.answer_document(document=file, caption=text, reply_markup=kb)


@router.message(F.document, AdminFSM.get_data)
async def main_block(message: Message, state: FSMContext):
    file_name = f"{os.getcwd()}/data.xlsx"
    await bot.download(file=message.document, destination=file_name)
    file_data = await xlsx_parser(file=file_name)
    state_data = await state.get_data()
    ozon_token = state_data["ozon_token"]
    client_id = state_data["client_id"]
    wait_msg = await message.answer("Ожидайте... ⏳")
    item_list = []
    for row in file_data:
        if row:
            price = await get_card_info(item_art=row[1])
            item = dict(sku=int(row[0]),
                        art=row[1],
                        price=price)
            item_list.append(item)
    errors_list = await ozon_api.clone_card(item_list=item_list, ozon_token=ozon_token, client_id=client_id)
    text = [f"Результаты клонирования:\n{'-' * 15}"]
    for row in file_data:
        if row:
            offer_id = f"РСВ-{row[1]}РСВ-{row[1]}"
            if len(errors_list) == 0:
                text.append(f"✅ РСВ-{row[1]}")
                continue
            for error in errors_list:
                if offer_id == error["offer_id"]:
                    text.append(f"⚠️ РСВ-{row[1]} || {error['error']}")
                    break
                else:
                    text.append(f"✅ РСВ-{row[1]}")
        else:
            text.append("❗️ Ошибка парсинга файла")
    kb = inline.home_kb()
    os.remove(file_name)
    await state.set_state(AdminFSM.home)
    await wait_msg.delete()
    await message.answer("\n".join(text), reply_markup=kb)

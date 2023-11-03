import asyncio
import os
import time

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram import F, Router
from aiogram.utils.markdown import hcode

from create_bot import bot, config
from .filters import AdminFilter
from .inline import AdminInlineKeyboard
from tgbot.misc.states import AdminFSM
from ...services.excel import xlsx_parser
from ...services.ozon_api import OzonAPI

router = Router()
router.message.filter(AdminFilter())

inline = AdminInlineKeyboard()

ozon_api = OzonAPI()

admin_group = config.tg_bot.admin_group


@router.message(Command("clone_ozon"))
async def main_block(message: Message, state: FSMContext):
    file_name = f'{os.getcwd()}/template.xlsx'
    file = FSInputFile(path=file_name, filename=file_name)
    text = "Заполните шаблон ссылками и загрузите в бот"
    await state.set_state(AdminFSM.get_data)
    await message.answer_document(document=file, caption=text)


@router.message(F.document, AdminFSM.get_data)
async def main_block(message: Message, state: FSMContext):
    file_name = f"{os.getcwd()}/data.xlsx"
    await bot.download(file=message.document, destination=file_name)
    file_data = await xlsx_parser(file=file_name)
    if len(file_data) == 0:
        await message.answer("Лист не должен быть пустым")
        return
    await message.answer("Ожидайте... ⏳")
    task_id = await ozon_api.clone_card(item_list=file_data)
    await message.answer(f"ID задачи {hcode(task_id)}\nПроверяем результаты клонирования ⏳")
    await asyncio.sleep(30)
    clone_result = await ozon_api.clone_status(task_id=task_id)
    await asyncio.sleep(1)
    if len(clone_result) > 0:
        text = f"{len(clone_result)} / {len(file_data)} товаров скопированы с ошибками. Запускается " \
               f"парсер\n<u>Внимание! процесс может занять длительное время. Пожалуйста, не прерывайте работу бота</u>"
        await message.answer(text)
    else:
        await message.answer("✅ Все товары скопированы")
        return
    error_items = [dict(offer_id=i["offer_id"], product_id=i["product_id"]) for i in clone_result]
    count_msg = await message.answer(f"Принудительно скопировано 0 / {len(error_items)} товаров")
    counter = 0
    for item in error_items:
        offer_id = item["offer_id"]
        product_id = item["product_id"]
        try:
            card_attrs = await ozon_api.get_card_attrs(offer_id=offer_id)
            time.sleep(9)
            await ozon_api.delete_cards(archive_item_list=[product_id], delete_item_list=[{"offer_id": offer_id}])
            images = [i["file_name"] for i in card_attrs["result"][0]["images"]]
            result = await ozon_api.create_card(income_data=card_attrs, images=images, price=str(2000))
            if result:
                counter += 1
                await count_msg.edit_text(f"Принудительно скопировано {counter} / {len(error_items)} товаров")
            else:
                await message.answer(f"{offer_id} не найден")
        except Exception as ex:
            await message.answer(f"{offer_id} error: {ex}")
    os.remove(file_name)
    await state.set_state(AdminFSM.home)
    text = "✅ Цикл завершён"
    await message.answer(text)

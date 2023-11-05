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
    if not task_id:
        await message.answer("Ошибка в файле")
        return
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
    archived_articles = []
    for item in error_items:
        offer_id = item["offer_id"]
        product_id = item["product_id"]
        if product_id == 0:
            await message.answer(f"{offer_id} не найден")
            continue
        try:
            card_attrs = await ozon_api.get_card_attrs(offer_id=offer_id)
            time.sleep(9)
            await ozon_api.delete_cards(archive_item=[product_id], delete_item=[{"offer_id": offer_id}])
            images = [i["file_name"] for i in card_attrs["result"][0]["images"]]
            result = await ozon_api.create_card(income_data=card_attrs, images=images, price=str(2000))
            counter += 1
            await count_msg.edit_text(f"Принудительно скопировано {counter} / {len(error_items)} товаров")
        except Exception as ex:
            await message.answer(f"{offer_id} error: {ex}")
    archived_items_chunks = ozon_api.paginator(item_list=archived_articles, size=20)
    for chunk in archived_items_chunks:
        text = ["Созданные ранее товары, сейчас в архиве:", "-" * 5]
        for item in chunk:
            text.append(hcode(item))
        await message.answer("\n".join(text))
    os.remove(file_name)
    await state.set_state(AdminFSM.home)
    text = "✅ Цикл завершён"
    await message.answer(text)

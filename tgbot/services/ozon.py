import asyncio
import json

import aiohttp

from create_bot import config

# ozon_token = config.misc.ozon_token
# ozon_client_id = config.misc.ozon_client_id


class OzonAPI:

    def __init__(self):
        pass

    @staticmethod
    async def __request(url: str, data: dict, ozon_token: str, client_id: int):
        headers = {
            'Content-Type': 'application/json',
            "Host": "api-seller.ozon.ru",
            "Api-Key": ozon_token,
            "Client-Id": client_id
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, headers=headers, data=data) as resp:
                return await resp.json()

    async def clone_card(self, item_list: list, ozon_token: str, client_id: int) -> list:
        url = "https://api-seller.ozon.ru/v1/product/import-by-sku"
        items = []
        for item in item_list:
            item_dict = dict(sku=item["sku"],
                             offer_id=f"РСВ-{item['art']}РСВ-{item['art']}",
                             currency_code="RUB",
                             old_price=str(item["price"]),
                             price=str(item["price"]),
                             vat="0")
            items.append(item_dict)
        data = dict(items=items)
        data = json.dumps(data)
        task = await self.__request(url=url, data=data, ozon_token=ozon_token, client_id=client_id)
        task_id = task["result"]["task_id"]
        await asyncio.sleep(30)
        result = await self.clone_status(task_id=int(task_id), ozon_token=ozon_token, client_id=client_id)
        items_result = result["result"]["items"]
        errors = []
        for item in items_result:
            if len(item["errors"]) > 0:
                errors.append(dict(offer_id=item["offer_id"], error=item["errors"][0]["code"]))
        return errors

    async def clone_status(self, task_id: int, ozon_token: str, client_id: int) -> dict:
        url = "https://api-seller.ozon.ru/v1/product/import/info"
        data = dict(task_id=task_id)
        data = json.dumps(data)
        result = await self.__request(url=url, data=data, ozon_token=ozon_token, client_id=client_id)
        return result

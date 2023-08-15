import asyncio

from bs4 import BeautifulSoup
import aiohttp

from create_bot import config

orecht_login = config.misc.orecht_login
orecht_pass = config.misc.orecht_pass


async def get_card_info(item_art: str):
    url = f'https://www.oreht.ru/modules.php?name=orehtPriceLS&op=ShowInfo&code={item_art}'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'referer': url
    }
    data = {'inn': orecht_login, 'pass': orecht_pass}
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, headers=headers, data=data) as resp:
            src = await resp.text()
    soup = BeautifulSoup(src, 'lxml')
    # stock_balance = soup.find(class_='mg-is-k').text
    try:
        price = soup.find(class_='mg-price').text.replace(',', '.').replace('\n', '')
        image = soup.find(class_="mg-glimage").find("img").get("src").strip()
        result = dict(price=int(float(price)), image=f"https://www.oreht.ru/{image}")
        return result
    except:
        return None

from typing import List

from openpyxl.reader.excel import load_workbook
from pydantic import BaseModel


class ExcelItem(BaseModel):
    ozon_id: int
    ozon_url: str
    article: str


async def xlsx_parser(file: str) -> List[ExcelItem]:
    wb = load_workbook(filename=file)
    sh = wb.active
    result = []
    for row in sh.iter_rows(min_row=2):
        try:
            ozon_id = row[0].value.split("/")[4].split("-")[-1]
            ozon_url = row[0].value
            article = row[1].value
            item = ExcelItem(ozon_id=ozon_id, ozon_url=ozon_url, article=article)
            result.append(item)
        except (AttributeError, Exception):
            result.append(None)
    return result

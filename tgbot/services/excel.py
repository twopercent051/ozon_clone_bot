from openpyxl.reader.excel import load_workbook


async def xlsx_parser(file: str):
    wb = load_workbook(filename=file)
    sh = wb.active
    result = []
    for row in sh.iter_rows(min_row=2):
        try:
            ozon_id = row[0].value.split("/")[4].split("-")[-1]
            ozon_url = row[0].value
            outer_id = None
            outer_source = None
            if "oreht.ru" in row[1].value.split("/")[2]:
                outer_id = row[1].value.split("=")[-1]
                outer_source = "orecht"
            if "unas.ru" in row[1].value.split("/")[2]:
                outer_id = row[1].value.split("/")[-2]
                outer_source = "unas"
            if outer_id and outer_source:
                item_dict = dict(ozon_id=ozon_id, ozon_url=ozon_url, outer_id=outer_id, outer_source=outer_source)
                result.append(item_dict)
        except (AttributeError, Exception):
            result.append(None)
    return result

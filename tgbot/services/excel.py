from openpyxl.reader.excel import load_workbook


async def xlsx_parser(file: str):
    wb = load_workbook(filename=file)
    sh = wb.active
    result = []
    for row in sh.iter_rows(min_row=2):
        try:
            ozon_id = row[0].value.split("/")[4].split("-")[-1]
            orecht_id = row[1].value.split("=")[-1]
            ozon_url = row[0].value
            result.append((ozon_id, orecht_id, ozon_url))
        except (AttributeError, Exception):
            result.append(None)
    return result

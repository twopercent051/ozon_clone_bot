from aiogram.fsm.state import State, StatesGroup


class AdminFSM(StatesGroup):
    home = State()
    client_id = State()
    api_token = State()
    get_data = State()

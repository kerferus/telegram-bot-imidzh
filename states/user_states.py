from aiogram.fsm.state import State, StatesGroup

class GiveawayStates(StatesGroup):
    waiting_for_consent = State()
    waiting_for_last_name = State()
    waiting_for_first_name = State()
    waiting_for_middle_name = State()
    waiting_for_phone = State()
    waiting_for_organization = State()
    waiting_for_activity = State()

class ConsultationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_company = State()
    waiting_for_description = State()
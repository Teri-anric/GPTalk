from aiogram.filters.callback_data import CallbackData


class SetProviderCallbackData(CallbackData, prefix="set_provider"):
    provider: str

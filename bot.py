import logging
import aiogram.utils.markdown as md

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode
from aiogram.dispatcher.filters import Text

from parser import num_round, exchange_rate

API_TOKEN = 'YOUR TOKEN'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    value = State()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await Form.value.set()

    await message.reply("Hi!\nI'm ConvertMoneyBot!\n")
    await message.reply('Enter your value')

@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    await state.finish()
    await message.reply('Cancelled', reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(
        lambda message: not message.text.isdigit(),
        state=Form.value)
async def process_value_invalid(message: types.Message, state: FSMContext):
    """
    If value input is invalid
    """
    return await message.reply('Your input must be a number')

@dp.message_handler(lambda message: message.text.isdigit(), state=Form.value)
async def proccess_value(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['value'] = int(message.text)

    await bot.send_message(message.chat.id,
        md.text(
            md.text(
                '{} USD = {} UAH'.format(
                    md.bold(data['value']),
                    md.bold(
                        num_round(
                            data['value'] * exchange_rate['USD']
                        )
                    )
                )
            ),
            md.text(
                '{} EUR = {} UAH'.format(
                    md.bold(data['value']),
                    md.bold(
                        num_round(
                            data['value'] * exchange_rate['EUR']
                            )
                        )
                    )
                ),
            md.text(
                '{} RUB = {} UAH'.format(
                    md.bold(data['value']),
                    md.bold(
                        num_round(
                            data['value'] * exchange_rate['RUB']
                        )
                    )
                )
            ),
            sep='\n'
        ),
        parse_mode=ParseMode.MARKDOWN
    )

    # End a loop after first input number
    # await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

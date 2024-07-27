import logging
import time

import aiohttp
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types.dice import DiceEmoji
from googletrans import Translator

from config_data.config import load_config
from database.database import Rating
from lexicon.lexicon import LEXICON

router = Router()
config = load_config()

logger = logging.getLogger(__name__)


@router.message(Command(commands='rating'))
async def cmd_rating(message: Message):
    # Проверяем, есть ли элементы в Rating
    if not Rating:
        await message.answer("Рейтинг пока пуст.")
        return

    # Инициализируем строку для результата
    res = "Рейтинг:\n"

    # Сортируем пользователей по рейтингу
    sorted_rating = sorted(Rating.values(), key=lambda x: x[1], reverse=True)

    # Проходим по отсортированным значениям и формируем сообщение
    for i, (user, score) in enumerate(sorted_rating, start=1):
        res += f"{i} место: {user} [{score}] балл(ов)\n"

    # Отправляем результат пользователю
    await message.answer(res)


@router.message(Command(commands='help'))
async def cmd_help(message: Message):
    await message.reply(LEXICON['/help'])


@router.message(Command(commands='contact'))
async def cmd_contact(message: Message):
    await message.answer(LEXICON['/contact'])


@router.message(Command(commands='random'))
async def cmd_random(message: Message):
    await message.reply_dice(emoji=DiceEmoji.DICE)


@router.message(Command(commands='fact'))
async def cmd_fact(message: Message):
    api_url = 'https://api.api-ninjas.com/v1/facts'

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(api_url, headers={'X-Api-Key': config.tg_bot.api_key}) as response:
                if response.status == 200:
                    data = await response.json()

                    if data:  # Проверяем, что ответ не пустой
                        fact = data[0]['fact']
                        translator = Translator()
                        translation = translator.translate(fact, dest="ru")
                        await message.reply(f'<b>{translation.text}</b>')
                    else:
                        await message.reply("Не удалось получить факт.")
                else:
                    await message.reply(LEXICON['error_fact'])
        except Exception as e:
            await message.reply("Произошла ошибка при попытке получить факт.")
            logger.info(f"Error fetching FACT: {e}")  # Логирование ошибки


@router.message(Command(commands='joke'))
async def cmd_joke(message: Message):
    api_url = 'https://api.api-ninjas.com/v1/jokes'

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(api_url, headers={'X-Api-Key': config.tg_bot.api_key}) as response:
                if response.status == 200:
                    data = await response.json()

                    if data:  # Проверяем, что ответ не пустой
                        jokes = data[0]['joke']
                        translator = Translator()
                        translation = translator.translate(jokes, dest="ru")
                        await message.reply(f'<b>{translation.text}</b>')
                    else:
                        await message.reply("Не удалось получить шутку.")
                else:
                    await message.reply(LEXICON['error_fact'])
        except Exception as e:
            await message.reply("Произошла ошибка при попытке получить шутку.")
            logger.info(f"Error fetching JOKE: {e}")  # Логирование ошибки


@router.message(Command(commands='riddles'))
async def cmd_riddles(message: Message):
    api_url = 'https://api.api-ninjas.com/v1/riddles'

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(api_url, headers={'X-Api-Key': config.tg_bot.api_key}) as response:
                if response.status == 200:
                    data = await response.json()

                    if data:  # Проверяем, что ответ не пустой
                        riddles = data[0]['question']
                        translator = Translator()
                        question = translator.translate(riddles, dest="ru")
                        answer = translator.translate(data[0]['answer'], dest="ru")
                        await message.reply(f'<b>{question.text}</b>\n\n'
                                            f'Ответ появится через 15 секунд')
                        time.sleep(15)
                        await message.reply(f'<b>{answer.text}</b>')
                    else:
                        await message.reply("Не удалось получить загадку.")
                else:
                    await message.reply(LEXICON['error_fact'])
        except Exception as e:
            await message.reply("Произошла ошибка при попытке получить загадку.")
            logger.info(f"Error fetching RIDDLE: {e}")  # Логирование ошибки

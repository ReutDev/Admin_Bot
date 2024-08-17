import asyncio
import logging

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


async def translate_text(text, dest_language):
    loop = asyncio.get_event_loop()
    translator = Translator()
    translation = await loop.run_in_executor(None, translator.translate, text, dest_language)
    return translation


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
                        try:
                            translation = await translate_text(fact, "ru")
                            if translation is not None and hasattr(translation, 'text'):
                                await message.reply(f'<b>{translation.text}</b>')
                            else:
                                await message.reply("Не удалось перевести факт 😞, попробуйте позже.")
                        except Exception as e:
                            logger.exception(f"Translation error: {e}")
                            await message.reply("Произошла ошибка при попытке перевести факт 😞, попробуйте позже.")
                    else:
                        await message.reply("Не удалось получить факт 😞, попробуйте позже.")
                else:
                    await message.reply(LEXICON['error_fact'])
        except Exception as e:
            await message.reply("Произошла ошибка при попытке получить факт 😞, попробуйте позже.")
            logger.info(f"Error fetching FACT: {e}")


@router.message(Command(commands='joke'))
async def cmd_joke(message: Message):
    api_url = 'https://api.api-ninjas.com/v1/jokes'

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(api_url, headers={'X-Api-Key': config.tg_bot.api_key}) as response:
                if response.status == 200:
                    data = await response.json()

                    if data:
                        jokes = data[0]['joke']
                        try:
                            translation = await translate_text(jokes, "ru")
                            if translation is not None and hasattr(translation, 'text'):
                                await message.reply(f'<b>{translation.text}</b>')
                            else:
                                await message.reply("Не удалось перевести шутку 😞, попробуйте позже.")
                        except Exception as e:
                            logger.exception(f"Translation error: {e}")
                            await message.reply("Произошла ошибка при попытке перевести шутку 😞, попробуйте позже.")
                    else:
                        await message.reply("Не удалось получить шутку 😞, попробуйте позже.")
                else:
                    await message.reply(LEXICON['error_fact'])
        except Exception as e:
            await message.reply("Произошла ошибка при попытке получить шутку 😞, попробуйте позже.")
            logger.info(f"Error fetching JOKE: {e}")


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
                        answer_text = data[0]['answer']

                        try:
                            question_translation = await translate_text(riddles, "ru")
                            answer_translation = await translate_text(answer_text, "ru")

                            if question_translation is not None and hasattr(question_translation, 'text') and \
                                    answer_translation is not None and hasattr(answer_translation, 'text'):
                                await message.reply(f'<b>{question_translation.text}</b>\n\n'
                                                    f'Ответ появится через 15 секунд')
                                await asyncio.sleep(15)
                                await message.reply(f'<b>{answer_translation.text}</b>')
                            else:
                                await message.reply("Не удалось перевести загадку 😞, попробуйте позже.")
                        except Exception as e:
                            logger.exception(f"Translation error: {e}")
                            await message.reply("Произошла ошибка при попытке перевести загадку 😞, попробуйте позже.")
                    else:
                        await message.reply("Не удалось получить загадку 😞, попробуйте позже.")
                else:
                    await message.reply(LEXICON['error_fact'])
        except Exception as e:
            await message.reply("Произошла ошибка при попытке получить загадку 😞, попробуйте позже.")
            logger.info(f"Error fetching RIDDLE: {e}")

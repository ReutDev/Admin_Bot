import logging

from aiogram import Router, F
from aiogram.types import Message, ContentType
from googletrans import Translator

from config_data.config import load_config
from database.database import Rating
from lexicon.lexicon import MATS, LEXICON
from services.services import IsAdmin
from services.services import correct_msg

router = Router()
config = load_config()

logger = logging.getLogger(__name__)


@router.message(IsAdmin(config.tg_bot.admin_ids))
async def check_text_on_mats(message: Message):
    user = message.from_user.id
    if user not in Rating:
        Rating[user] = [message.from_user.first_name, 0]
    message_type = message.content_type
    if message_type == ContentType.PHOTO and message.caption:
        Rating[user][1] += len(message.caption.split())
    if message_type == ContentType.TEXT:
        Rating[user][1] += len(message.text.split())


@router.message(lambda msg: msg.text.lower() in ['привет', '/start'])
async def check_text_on_mats(message: Message):
    await message.answer(LEXICON['hello'])


@router.message(F.text)
async def check_text_on_mats(message: Message):
    user = message.from_user.id

    if user not in Rating:
        Rating[user] = [message.from_user.first_name, 0]

    text = message.text
    translator = Translator()
    translation = translator.translate(text, dest="ru")
    res = translation.text.split()
    answer = translation.text.split()
    valid = 1

    for i, word in enumerate(res, 0):
        if correct_msg(word.upper()) in MATS:
            valid = 0
            Rating[user][1] -= 10
            if message.from_user.first_name.lower() == 'булат':
                await message.delete()
                await message.answer(text=LEXICON['mat_bulat'])
                return
            if message.from_user.first_name.lower() == 'саят':
                await message.delete()
                await message.answer(text=LEXICON['mat_sayat'])
                return
            answer[i] = '*' * len(word)
    if not valid:
        await message.delete()
        await message.answer(text=f'{message.from_user.first_name} хотел сказать: {' '.join(answer)}')

    Rating[user][1] += len(text.split())


@router.message(F.photo)
async def check_photo_on_mats(message: Message):
    user = message.from_user.id

    if user not in Rating:
        Rating[user] = [message.from_user.first_name, 0]

    text = message.caption
    translator = Translator()
    translation = translator.translate(text, dest="ru")
    res = translation.text.split()
    answer = translation.text.split()
    valid = 1

    for i, word in enumerate(res, 0):
        if correct_msg(word.upper()) in MATS:
            valid = 0
            Rating[user][1] -= 10
            if message.from_user.first_name.lower() == 'булат':
                await message.delete()
                await message.answer(text=LEXICON['mat_bulat'])
                return
            if message.from_user.first_name.lower() == 'саят':
                await message.delete()
                await message.answer(text=LEXICON['mat_sayat'])
                return
            answer[i] = '*' * len(word)
    if not valid:
        await message.delete()
        await message.bot.send_photo(chat_id=message.chat.id, photo=message.photo[-1].file_id,
                                     caption=f'{message.from_user.first_name} хотел сказать: {' '.join(answer)}')

    Rating[user][1] += len(text.split())

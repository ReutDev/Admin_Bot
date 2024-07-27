import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from config_data.config import load_config
from handlers import user_handlers, other_handlers
from keyboards.main_menu import set_main_menu

# Инициализируем логгер
logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main():
    # Конфигурируем логирование
    logging.basicConfig(level=logging.INFO)
    formatter = logging.Formatter('%(filename)s:%(lineno)d #%(levelname)-8s '
                                  '[%(asctime)s] - %(name)s - %(message)s')
    file_handler = logging.FileHandler('bot_logs.log', mode='w', encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # Загружаем конфиг в переменную config
    config = load_config('.env')
    # Инициализируем объект хранилища
    # storage = ...

    # Инициализируем бот и диспетчер
    default = DefaultBotProperties(parse_mode='HTML')

    bot = Bot(token=config.tg_bot.token, default=default)
    dp = Dispatcher()

    # Инициализируем другие объекты (пул соединений с БД, кеш и т.п.)
    # ...

    # Помещаем нужные объекты в workflow_data диспетчера
    dp.workflow_data.update(
        {'token': config.tg_bot.token, 'admin_ids': config.tg_bot.admin_ids, 'api_token': config.tg_bot.api_key})

    # Настраиваем главное меню бота
    await set_main_menu(bot)

    # Регистриуем роутеры
    logger.info('Подключаем роутеры')
    dp.include_router(other_handlers.router)
    dp.include_router(user_handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

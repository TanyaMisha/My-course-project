import requests                              # импортируем библиотеку requests
import datetime                              # импотируем модуль datetime
from config import tg_bot_token              # из файла config.py забираем нашу переменную с токеном
from aiogram import Bot, types               # из библиотеки импортируем бота, типы
from aiogram.dispatcher import Dispatcher    # из библиотеки импортируем диспетчер (управление handler)
from aiogram.utils import executor           # из библиотеки импортируем executor
from config import open_weather_token        # импортируем токен сервиса OpenWeather
from aiogram.dispatcher.filters import Text
from asyncio import sleep
# from pprint import pprint                  # для удобного вывода ответа запроса (словаря, погода)


bot = Bot(token=tg_bot_token)                   # создаем экземпляр бота
dp = Dispatcher(bot)                            # создаем объект диспетчера (в aiogram)

@dp.message_handler(commands=["start"])         # функция, обрабатывающая команду /start
async def cmd_start(message: types.Message):    # создаем кнопки
    kb = [
        [types.KeyboardButton(text="Погода")],
        [types.KeyboardButton(text="Игра в кости")],
        [types.KeyboardButton(text="Цитата дня")]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True     # чтобы кнопки были меньше размером, применили resize
    )
    await message.answer(f'Привет, {message.from_user.username}! Что выбираете?', reply_markup=keyboard)


@dp.message_handler(Text("Игра в кости"))       # создаем обработчика событий
async def on_message(message: types.Message):
    await bot.send_message(message.from_user.id, f" Итак, {message.from_user.username}, начинаем игру!")
    await sleep(1)                       # отложит следующее событие на 1 сек

    await bot.send_message(message.from_user.id, "Ход бота")
    bot_data = await bot.send_dice(message.from_user.id)    # отправляет кубик из библиотеки aiogram
    bot_data = bot_data['dice']['value']
    #print(bot_data['dice']['value'])    # распечатает в консоль число точек, выпавшее на кубике
    await sleep(5)                       # отложит следующее событие на 5 сек

    await bot.send_message(message.from_user.id, f"{message.from_user.username}, Ваш ход")
    user_data = await bot.send_dice(message.from_user.id)
    user_data = user_data['dice']['value']
    # print(bot_data['dice']['value'])    # распечатает в консоль число точек, выпавшее на кубике
    await sleep(5)                        # отложит следующее событие на 5 сек

    if bot_data > user_data:
        await bot.send_message(message.from_user.id, "Вы проиграли! \U00002620")
        await bot.send_message(message.from_user.id, "Не расстраивайтесь! Сыграйте еще раз и Вам обязательно повезет!")
        await sleep(2)                    # отложит следующее событие на 2 сек

    elif bot_data < user_data:
        await bot.send_message(message.from_user.id, "Вы победили!")
        await bot.send_message(message.from_user.id, "Удача - Ваше второе имя! \U0001F600 Поздравляю!")
        await sleep(2)                    # отложит следующее событие на 2 сек


    else:
        await bot.send_message(message.from_user.id, "Ничья!")
        await sleep(2)                    # отложит следующее событие на 2 сек

    await bot.send_message(message.from_user.id, "Сыграйте еще раз или выберите что-то другое")

@dp.message_handler(Text("Цитата дня"))             # создаем обработчика событий
async def get_quote(message: types.Message):
    await bot.send_message(message.from_user.id, "Ваша цитата дня")
    await sleep(1)                       # отложит следующее событие на 1 сек
    try:                                 # делаем запрос, получаем и обрабатываем данные
        r = requests.get(
            "https://favqs.com/api/qotd"
        )
        data = r.json()                 # этой функцией декодируем данные в формате json
        author = data["quote"]["author"]
        quote = data["quote"]["body"]

        await message.reply(f"Автор: {author}\nЦитата: {quote}")
        await sleep(2)

    except:
        await message.reply("\U00002620 Ошибка \U00002620")    # обрабатываем ошибку
        await sleep(2)

    await bot.send_message(message.from_user.id, "Если желаете продолжить, выберите одну из кнопок")


@dp.message_handler(Text("Погода"))                         # создаем обработчика событий
async def weather(message: types.Message):                  # создаем функцию, передаем в ней 2 параметра
    await message.answer('Введите название города'.format(message.from_user))


@dp.message_handler()                        # создаем эмоджи
async def get_weather(message: types.Message):
    code_to_smile = {
        "Clear": "Ясно \U00002600",
        "Clouds": "Облачно \U00002601",
        "Rain": "Дождь \U00002614",
        "Drizzle": "Дождь \U00002614",
        "Thunderstorm": "Гроза \U000026A1",
        "Snow": "Снег \U0001F328",
        "Mist": "Туман \U0001F32B"
    }

    try:                             #  в этом блоке делаем запрос, получаем и обрабатываем данные
        r = requests.get(            # создаем переменную и формируем запрос
            f"http://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={open_weather_token}&units=metric"
        )                            # использовали параметр units из документации для перевода в метрич.сист.измер.
        data = r.json()              # этой функцией декодируем данные в формате json
        # pprint(data)               # распечатаем ответ запроса (словарь)

        city = data["name"]          # обращаемся к ключу name и получаем название города
        cur_weather = data["main"]["temp"]  # обращаемся к ключу temp из блока main и получаем температуру

        weather_description = data["weather"][0]["main"]   # забрали main-значение
        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]        # при совпадении значений с ключами словаря с эмоджи
        else:
            wd = "Лучше уточните - посмотрите в окно!"     # при  не совпадении значений с ключами словаря с эмоджи

        humidity = data["main"]["humidity"]   # влажность
        pressure = data["main"]["pressure"]   # давление
        wind = data["wind"]["speed"]          # скорость ветра
        sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])   # время рассвета
        sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])     # время заката
        length_of_the_day = datetime.datetime.fromtimestamp(data["sys"]["sunset"]) - datetime.datetime.fromtimestamp(
            data["sys"]["sunrise"])            # долгота дня

        await message.reply(f"***{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}***\n"
              f"Погода в городе: {city}\nТемпература: {cur_weather}C° {wd}\n"
              f"Влажность: {humidity}%\nДавление: {pressure} мм.рт.ст\nВетер: {wind} м/с\n"
              f"Восход солнца: {sunrise_timestamp}\nЗакат солнца: {sunset_timestamp}\nПродолжительность дня: {length_of_the_day}\n"
              f"***Хорошего дня!***"
              )
        await sleep(1)                        # отложит следующее событие на 1 сек

    except:
        await message.reply("\U00002620 Проверьте название города \U00002620")   # обрабатываем ошибку названия города

    await bot.send_message(message.from_user.id, "Еще о погоде или выберите что-то другое")


if __name__ == '__main__':          # запускаем бота
    executor.start_polling(dp)


















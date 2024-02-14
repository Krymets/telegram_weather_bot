import json
import requests
import config
import logging
from aiogram import Bot, Dispatcher, executor, types

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

w = ['погода', 'weather']

@dp.message_handler()
async def echo(message: types.Message):
    for i in w:
        if i in message.text.lower():
            text = message.text.split()
            for _ in text:
                _ = _.replace(',', '').replace('.', '').replace(':', '').replace(';', '').replace('"', '').replace("'", '')
                if _.lower() != i:
                    await message.answer(await get_weather_func(_))

async def get_weather_func(text):
    response_get_weather = requests.get(config.weather_api.format(city=text))
    if response_get_weather.status_code != 200:
        return 'Вибач, але такого міста я не знаю :('
    else:
        data = json.loads(response_get_weather.content)
        print(data)
        beautiful_city_name = data['name']
        temp = round(data['main']['temp'] - 273.15)
        feels_like = round(data['main']['feels_like'] - 273.15)
        mess = presentation(temp, feels_like, beautiful_city_name)
        return mess


def presentation(temp, feels_like, beautiful_city_name):
    if temp > 0:
        temp = f'+{str(temp)}'
    if feels_like > 0:
        feels_like = f'+{str(feels_like)}'
    return f'{beautiful_city_name}\nЗараз температура {temp} градусів\nВідчувається як {feels_like}'


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

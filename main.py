import json
import requests
import config
import logging
from aiogram import Bot, Dispatcher, executor, types

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

# List of keywords
keywords = ['weather', 'forecast', 'погода']


# Function to clean text by removing punctuation and converting to lowercase
def clean_text(word: str) -> str:
    return word.translate(str.maketrans('', '', ',.:;"\'')).lower()


@dp.message_handler()
async def echo(message: types.Message):
    # Split the message text into words and clean them
    words = [clean_text(word) for word in message.text.split()]

    # Check if any of the keywords are in the message
    for keyword in keywords:
        if keyword in words:
            # Remove the keyword and process the remaining words
            other_words = [word for word in words if word != keyword]

            # Call the weather function for each remaining word
            for word in other_words:
                response = await get_weather_func(word)
                await message.answer(response)


async def get_weather_func(text):
    response_get_weather = requests.get(config.weather_api.format(city=text))
    if response_get_weather.status_code != 200:
        return "Sorry, but I don't know such a city"
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
    return f'{beautiful_city_name}\nThe temperature now {temp} degrees\nFeels like {feels_like}'


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

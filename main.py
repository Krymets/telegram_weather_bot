import requests
import config
import logging
from aiogram import Bot, Dispatcher, executor, types

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

# List of keywords to trigger weather request
keywords = ['weather', 'forecast']


# Utility function to clean up words (lowercase and remove punctuation)
def clean_text(word: str) -> str:
    return word.translate(str.maketrans('', '', ',.:;"\'!?')).lower()


@dp.message_handler()
async def echo(message: types.Message):
    words = [clean_text(word) for word in message.text.split()]
    if any(keyword in words for keyword in keywords):
        city_candidates = [word for word in words if word not in keywords]
        if not city_candidates:
            await message.answer("Please specify a city to get the weather information.")
            return

        for city in city_candidates:
            response = await get_weather_func(city)
            await message.answer(response)


async def get_weather_func(city_name: str) -> str:
    try:
        response = requests.get(config.weather_api.format(city=city_name), timeout=10)
        response.raise_for_status()

        data = response.json()

        if 'main' not in data or 'name' not in data or 'weather' not in data:
            logging.error(f"Unexpected API response format: {data}")
            return "Sorry, I couldn't find the weather information for that city."

        city = data['name']
        temp = round(data['main']['temp'] - 273.15)
        feels_like = round(data['main']['feels_like'] - 273.15)
        description = data['weather'][0]['description'].capitalize()
        emoji = get_weather_emoji(description)

        return format_weather(city, temp, feels_like, description, emoji)

    except requests.exceptions.RequestException as e:
        logging.error(f"Error while fetching weather data: {e}")
        return "Sorry, there was an error fetching the weather information. Please try again later."

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return "An unexpected error occurred. Please try again."


def get_weather_emoji(description: str) -> str:
    desc = description.lower()
    if 'clear' in desc:
        return '☀️'
    elif 'cloud' in desc:
        return '☁️'
    elif 'rain' in desc:
        return '🌧️'
    elif 'snow' in desc:
        return '❄️'
    elif 'thunder' in desc:
        return '⛈️'
    elif 'fog' in desc or 'mist' in desc:
        return '🌫️'
    return '🌡️'


def format_weather(city: str, temp: int, feels_like: int, description: str, emoji: str) -> str:
    temp_str = f'+{temp}' if temp > 0 else str(temp)
    feels_like_str = f'+{feels_like}' if feels_like > 0 else str(feels_like)
    return (
        f"{emoji} *Weather in {city}*\n"
        f"Description: {description}\n"
        f"Temperature: {temp_str}°C\n"
        f"Feels like: {feels_like_str}°C"
    )


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

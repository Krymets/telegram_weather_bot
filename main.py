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


async def get_weather_func(city_name: str) -> str:
    try:
        # Make the API call
        response = requests.get(config.weather_api.format(city=city_name), timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses

        # Parse JSON data
        data = response.json()

        # Validate response content
        if 'main' not in data or 'name' not in data:
            logging.error(f"Unexpected API response format: {data}")
            return "Sorry, I couldn't find the weather information for this city."

        # Extract relevant data
        beautiful_city_name = data['name']
        temp = round(data['main']['temp'] - 273.15)
        feels_like = round(data['main']['feels_like'] - 273.15)

        return presentation(temp, feels_like, beautiful_city_name)

    except requests.exceptions.RequestException as e:
        logging.error(f"Error while fetching weather data: {e}")
        return "Sorry, there was an error fetching the weather information. Please try again later"

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return "An unexpected error occurred. Please try again"


def presentation(temp: int, feels_like: int, city_name: str) -> str:
    temp = f'+{temp}' if temp > 0 else str(temp)
    feels_like = f'+{feels_like}' if feels_like > 0 else str(feels_like)
    return (f'{city_name}\n'
            f'Temperature: {temp}°C\n'
            f'Feels like: {feels_like}°C')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

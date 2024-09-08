from pathlib import Path
from configparser import ConfigParser
import aiohttp
import asyncio
import typer

# constants
API_CONFIG_SECTION = "api_config"
DATABASE_API_CONFIG_SECTION = "database_api_config"
HOST_CONFIG_FIELD = "host"
PORT_CONFIG_FIELD = "port"
TRIVIA_CONFIG_PATH = Path(__file__).parent / "trivia_api" / "trivia_config.ini"

# config
config = ConfigParser()
config.read(str(TRIVIA_CONFIG_PATH))
CALLBACK_URL = f"http://{config.get(API_CONFIG_SECTION, HOST_CONFIG_FIELD)}:" \
               f"{config.get(API_CONFIG_SECTION, PORT_CONFIG_FIELD)}/trivia"

app = typer.Typer(name="trivia generator")


async def send_to_database(session: aiohttp.ClientSession, question_data: dict):
    """
    Asynchronously sends a trivia question to the database.

    :param session: aiohttp session object
    :param question_data: question data to send
    :return: response status or error
    """
    # checking of the values will be required
    async with session.post(f"http://{config.get(DATABASE_API_CONFIG_SECTION, HOST_CONFIG_FIELD)}:"
                            f"{config.get(DATABASE_API_CONFIG_SECTION, PORT_CONFIG_FIELD)}/database",
                            json=question_data) as response:
        # logging!!!
        if response.status == 202:
            print(f"Successfully sent question: {question_data}")
        else:
            print(f"Failed to send question: {question_data}, Status Code: {response.status}")


async def fetch_question(session: aiohttp.ClientSession, category: str):
    """
    Asynchronously fetches a trivia question from the API.

    :param session: aiohttp session object
    :param category: category for the trivia question
    :return: JSON response from the API
    """
    async with session.get(CALLBACK_URL, params={"category": category}) as response:
        if response.status == 200:
            return await response.json()
        else:
            return None


@app.command("generate")
def generate(category: str, question_number: int = 10):
    """
    Generates a number of questions for a category given by user and sends them over to a database.

    :param category: category for trivia questions
    :param question_number: number of questions to be generated
    :return: None
    """
    asyncio.run(generate_questions(category, question_number))


async def generate_questions(category: str, question_number: int):
    """
    Asynchronously generate multiple questions for a given category.

    :param category: category for trivia questions
    :param question_number: number of questions to generate
    :return: None
    """
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_question(session, category) for _ in range(question_number)]
        results = await asyncio.gather(*tasks)

        for result in results:
            if result is not None:
                await send_to_database(session, result)


if __name__ == "__main__":
    app()

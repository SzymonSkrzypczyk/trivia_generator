from pathlib import Path
from configparser import ConfigParser
import aiohttp
import asyncio
import typer

from common import Logger, ConfigReader

# constants
API_CONFIG_SECTION = "api_config"
DATABASE_API_CONFIG_SECTION = "database_api_config"
HOST_CONFIG_FIELD = "host"
PORT_CONFIG_FIELD = "port"
TRIVIA_CONFIG_PATH = Path(__file__).parent / "trivia_config.ini"
TRIVIA_GENERATOR_LOG_FILE = Path(__file__).parent / "logs" / "trivia_generator.log"

# load logger
logger = Logger(str(TRIVIA_GENERATOR_LOG_FILE))

# config
config = ConfigReader(str(TRIVIA_CONFIG_PATH), logger)
# host and port for trivia api
HOST_TRIVIA = config.get_field(API_CONFIG_SECTION, HOST_CONFIG_FIELD)
PORT_TRIVIA = config.get_field(API_CONFIG_SECTION, PORT_CONFIG_FIELD)
# host and port for database API
HOST_TARGET = config.get_field(DATABASE_API_CONFIG_SECTION, HOST_CONFIG_FIELD)
PORT_TARGET = config.get_field(DATABASE_API_CONFIG_SECTION, PORT_CONFIG_FIELD)

if None in (HOST_TRIVIA, PORT_TRIVIA, PORT_TARGET, HOST_TARGET):
    logger.log_exit("Empty value in the config file - trivia generator")
CALLBACK_URL = f"http://{HOST_TRIVIA}:{PORT_TRIVIA}/trivia"

app = typer.Typer(name="trivia generator")


async def send_to_database(session: aiohttp.ClientSession, question_data: dict):
    """
    Asynchronously sends a trivia question to the database.

    :param session: aiohttp session object
    :param question_data: question data to send
    :return: response status or error
    """
    # checking of the values will be required
    try:
        async with session.post(f"http://{HOST_TARGET}:{PORT_TARGET}/database",
                                json=question_data) as response:
            if response.status == 202:
                logger.log_info(f"Successfully sent question: {question_data}")
            else:
                logger.log_error(RuntimeError("Failed to send question"),
                                 f"Failed to send question: {question_data}, Status Code: {response.status}")
    except aiohttp.ClientError as e:
        logger.log_error(e, "Network error while sending question to database")
    except Exception as e:
        logger.log_error(e, "Unexpected error while sending question")


async def fetch_question(session: aiohttp.ClientSession, category: str):
    """
    Asynchronously fetches a trivia question from the API.

    :param session: aiohttp session object
    :param category: category for the trivia question
    :return: JSON response from the API
    """
    try:
        async with session.get(CALLBACK_URL, params={"category": category}, timeout=15) as response:
            if response.status == 200:
                return await response.json()
            else:
                logger.log_error(RuntimeError("Unsuccessful generation"),
                                 f"Failed to fetch question for category {category},"
                                 f" Status Code: {response.status}")
                return None
    except aiohttp.ClientError as e:
        logger.log_error(e, "Network error while fetching question")
    except asyncio.TimeoutError as e:
        logger.log_error(e, f"Timeout while fetching question for category {category}")
    except Exception as e:
        logger.log_error(e, "Unexpected error while fetching question")
    return None


@app.command("generate")
def generate(category: str, question_number: int = 10):
    """
    Generates a number of questions for a category given by user and sends them over to a database.

    :param category: category for trivia questions
    :param question_number: number of questions to be generated
    :return: None
    """
    try:
        asyncio.run(generate_questions(category, question_number))
    except Exception as e:
        logger.log_error(e, "Error occurred during question generation")


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

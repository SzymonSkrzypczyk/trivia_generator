from configparser import ConfigParser
from pathlib import Path
import fastapi
from uvicorn import run
from pydantic import BaseModel
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers.string import StrOutputParser

"""
To do: 
- class for loading and validating config
- class for logging
- logging 

"""

# constants
API_CONFIG_SECTION = "api_config"
MODEL_CONFIG_SECTION = "model_config"
HOST_CONFIG_FIELD = "host"
PORT_CONFIG_FIELD = "port"
MODEL_CONFIG_FIELD = "model"
TRIVIA_CONFIG_PATH = Path(__file__).parent / "trivia_config.ini"

# load config
config = ConfigParser()
config.read(str(TRIVIA_CONFIG_PATH))


class Question(BaseModel):
    """
    Data model for a question generated by the chain, to be used by API
    """
    question: str
    answer_a: str
    answer_b: str
    answer_c: str
    answer_d: str
    correct_answer: str


# AI's components
# defined once at the start of the execution
# out of its simplicity it's not contained by any function or method
llm = Ollama(model=config.get(MODEL_CONFIG_SECTION, MODEL_CONFIG_FIELD))
prompt = PromptTemplate.from_template(
    "You are a trivia questions generator. For a given category: {category}, generate a question about this topic and "
    "return it in the following CSV format: "
    "'question', 'answer_a', 'answer_b', 'answer_c', 'answer_d', 'correct_answer'."
    "For example, for the topic 'countries':"
    "'What is the capital of Poland?', 'Warsaw', 'Berlin', 'Paris', 'Oslo', 'Warsaw'."
    "Only return the answer in CSV format, with values separated by commas, and nothing else. The correct answer"
    "should be the same text that an answer to be chosen has. Also do not include any quotes in the string you return."
    "Remember to only return the question and nothing more!"
)
chain = prompt | llm | StrOutputParser()

app = fastapi.FastAPI(title="Trivia Generator", description="An API that generates a trivia question for a given "
                                                            "category")


@app.get("/trivia", response_model=Question)
async def generate_question(category: str) -> Question | fastapi.HTTPException:
    """
    API endpoint asynchronously returning generated question for a category given by an user

    :param category: Category of the trivia question
    :return: Either an error if there is a problem with a given category or generated data or a fully generated question
    :rtype: Question | fastapi.HTTPException
    """
    if category == "":
        return fastapi.HTTPException(400, "You have to provide a correct category!")

    data = await chain.ainvoke({"category": category})
    data = data.split(",")

    if len(data) != 6:
        return fastapi.HTTPException(500, "Internal problem with generating data!")

    return Question(
        question=data[0],
        answer_a=data[1],
        answer_b=data[2],
        answer_c=data[3],
        answer_d=data[4],
        correct_answer=data[5]
    )

if __name__ == '__main__':
    # run the api
    # config values will be later extended
    run(
        app,
        host=config.get(API_CONFIG_SECTION, HOST_CONFIG_FIELD),
        port=int(config.get(API_CONFIG_SECTION, PORT_CONFIG_FIELD)),
    )

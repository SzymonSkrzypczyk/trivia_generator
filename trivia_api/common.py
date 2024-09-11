import re
from string import Template
import configparser
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
from configparser import ConfigParser

# constants
MSG_FILE_NOT_EXISTENT = "You have to provide an existing file."
MSG_NO_SUCH_OPTION = Template("No such option has been found for $section.$parameter")
MSG_RETRIEVING_VALUE = Template("Retrieving value for $section.$parameter")
MSG_EMPTY_FIELD = Template("Config fields cannot be empty: $section.$parameter")
MSG_EMPTY_VALUE_SET = Template("You cannot set empty value for a parameter for $section.$parameter")


class Logger:
    def __init__(self, log_file: Path | str):
        self.log_path = Path(log_file)
        self.logger = self.load_logger(self.log_path)

    @staticmethod
    def load_logger(path: Path | str) -> logging.Logger:
        path = Path(path)

        # create the path if it does not exist
        path.touch(exist_ok=True)

        # create logger
        logger = logging.getLogger("TriviaLogger")
        logger.setLevel(logging.INFO)
        # create formatter and rotating file handler
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s", "%Y/%m/%d %H:%M:%S")
        file_handler = RotatingFileHandler(path, maxBytes=1000000, backupCount=8)
        file_handler.setFormatter(formatter)
        # register handler
        logger.addHandler(file_handler)

        # return logger
        return logger

    def log_info(self, message: str):
        self.logger.info("")
        self.logger.info(message)
        self.logger.info("")

    def log_error(self, exception: BaseException, message: str = None):
        self.logger.info("")
        self.logger.exception(exception)
        if message is not None:
            self.logger.error(message)
        self.logger.info("")

    def log(self, message: str, level: int):
        self.logger.info("")
        self.logger.log(level, message)
        self.logger.info("")

    def log_exit(self, message: str, level: int = logging.INFO):
        self.logger.info("")
        self.logger.log(level, message)
        # if level is different than info exit with code 1
        if level != logging.INFO:
            exit(1)
        exit(0)


class ConfigReader:
    def __init__(self, config_file: Path | str, logger: Logger):
        self.config_path = Path(config_file)
        self.logger = logger
        self.config = self.load_config(self.config_path)
        self.logger.log_info("Config loaded successfully!")

    @staticmethod
    def load_config(path: Path | str) -> ConfigParser:
        path = Path(path)

        # check if a given path exists
        if not path.exists():
            raise FileNotFoundError(MSG_FILE_NOT_EXISTENT)

        conf = ConfigParser()
        conf.read(path)

        return conf

    def get_field(self, section: str, parameter: str) -> str:
        try:
            val = self.config.get(section, parameter)
            self.logger.log_info(MSG_RETRIEVING_VALUE.substitute(section=section, parameter=parameter))

        except configparser.NoOptionError as e:
            self.logger.log_error(e, MSG_NO_SUCH_OPTION.substitute(section=section, parameter=parameter))
            self.logger.log_exit("Leaving...", logging.ERROR)

        except ValueError as e:
            self.logger.log_error(e, MSG_EMPTY_FIELD.substitute(section=section, parameter=parameter))
            self.logger.log_exit("Leaving...", logging.ERROR)

        except Exception as e:
            self.logger.log_error(e)
            self.logger.log_exit("Leaving...", logging.ERROR)

        return val

    def set_field(self, section: str, parameter: str, value: str) -> bool:
        try:
            if not value:
                raise ValueError(MSG_EMPTY_VALUE_SET.substitute(section=section, parameter=parameter))
            self.config.set(section, parameter, value)
            # replace values in the config file
            text = self.config_path.read_text()
            text = re.sub(f"{parameter}=", f"{parameter}={value}", text)
            self.config_path.write_text(text)

        except ValueError as e:
            self.logger.log_error(e, "Empty value provided")
            return False

        except configparser.NoOptionError as e:
            self.logger.log_error(e, MSG_NO_SUCH_OPTION.substitute(section=section, parameter=parameter))
            return False

        except Exception as e:
            self.logger.log_error(e)
            return False

        return True

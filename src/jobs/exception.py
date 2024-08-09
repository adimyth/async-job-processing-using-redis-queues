from loguru import logger

from src.jobs.base import BaseJob


class FailedJob(BaseJob):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def handle(self):
        logger.info("Running FailedJob")

        raise MyException


class MyException(Exception):
    def __init__(self, message="This is a custom exception") -> None:
        self.message = message
        super().__init__(self.message)

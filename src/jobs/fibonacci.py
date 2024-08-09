from loguru import logger

from src.jobs.base import BaseJob


class Fibonacci(BaseJob):
    def __init__(self, n: int, **kwargs):
        super().__init__(**kwargs)
        self.n = n

    def handle(self):
        logger.info(f"Calculating Fibonacci number for n={self.n}")

        if self.n < 0:
            raise ValueError("n must be non-negative")
        elif self.n <= 1:
            return self.n
        else:
            a, b = 0, 1
            for _ in range(2, self.n + 1):
                a, b = b, a + b
            return b

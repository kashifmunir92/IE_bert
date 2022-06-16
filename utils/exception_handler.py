import traceback
from functools import wraps

from utils.logger import logger


def catch_exception(function):
    @wraps(function)
    def inner(*args, **kwargs):
        try:
            # print("当前运行方法", function.__name__)
            return function(*args, **kwargs)
        except Exception as e:
            logger.error(f"{function.__name__} is error,here are details:{traceback.format_exc()}")

    return inner

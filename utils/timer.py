import datetime

from utils.logger import logger


def time_cost(func):
    def inner(*args, **kwargs):
        start_time = datetime.datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.datetime.now()
        # print()
        logger.info(f'当前函数名称：{func.__name__} | 时间消耗:{end_time - start_time}')
        return result

    return inner

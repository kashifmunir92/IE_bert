import sys
import logging
import os
import pathlib
import sys
from logging import Formatter, StreamHandler
from logging.handlers import WatchedFileHandler

logging_name_to_Level = {
    'CRITICAL': logging.CRITICAL,
    'FATAL': logging.FATAL,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'NOTSET': logging.NOTSET,
}


def get_logger(log_path, log_level: str, name='mylogger'):
    """
    获取日志实例
    Args:
        log_path:    日志目录
        log_level:   日志级别
        name:        日志记录器的名字
    Returns:
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging_name_to_Level.get(log_level.upper(), logging.INFO))

    # 可以将日志写到任意位置(handlers)
    default_handlers = {
        WatchedFileHandler(os.path.join(log_path, 'all.log')): logging.INFO,  # 所有日志
        WatchedFileHandler(os.path.join(log_path, 'error.log')): logging.ERROR,  # 错误日志
        StreamHandler(sys.stdout): logging.DEBUG  # 控制台
    }

    # 日志格式：[时间] [文件名-行号] [类型] [信息]
    _format = '%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d] %(message)s - %(process)d-%(thread)d'
    # 添加多个位置
    for handler, level in default_handlers.items():
        handler.setFormatter(Formatter(_format))
        if level is not None:
            handler.setLevel(level)
        logger.addHandler(handler)
    return logger


log_path = './logs'  # pylint: disable=C0103

log_level = 'INFO'  # pylint: disable=C0103
# log_path = BASE_DIR.joinpath(log_path)
log_path = pathlib.Path(log_path)
if not log_path.exists():
    log_path.mkdir(parents=True)
logger = get_logger(log_path, log_level)
# 设置模式
DEBUG = log_level == 'INFO'

import sys
import datetime
import logging.handlers


def create_logger(logger_name=None, stream_level=logging.DEBUG, file_level=logging.DEBUG, file_name="debug.log"):
    # logger instance 생성
    logger = logging.getLogger(logger_name)

    # logger level 설정
    logger.setLevel(logging.DEBUG)

    # formatter instance 생성
    log_format = "[%(levelname)+8s|%(filename)+25s:%(lineno)+4s] %(asctime)s > %(message)s"
    formatter = logging.Formatter(log_format)

    # handler instance 생성
    stream_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(file_name)

    # handler level 설정
    stream_handler.setLevel(stream_level)
    file_handler.setLevel(file_level)

    # handler format 설정
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # logger handler 추가
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger


now = datetime.datetime.today()
log_file_name = str(now.year) + (str(now.month)).zfill(2) + (str(now.day)).zfill(2) + ".txt"
logger = create_logger(
    logger_name="auto_bot_logger",
    file_name=log_file_name
)

if __name__ == "__main__":
    pass
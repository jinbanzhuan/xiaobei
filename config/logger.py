import logging
import os
import sys
from datetime import datetime


def get_logger(name=None):
    logger = logging.getLogger(name or "xiaobei")

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)

    # 文件处理器 - 实时刷新配置
    file_handler = logging.FileHandler(
        os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log"),
        encoding="utf-8",
        mode='a'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # 设置为无缓冲模式，确保日志实时写入
    file_handler.stream.reconfigure(line_buffering=True)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    fmt = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(fmt)
    console_handler.setFormatter(fmt)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False

    return logger
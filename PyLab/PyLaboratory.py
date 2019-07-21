# _*_coding:utf-8_*_
from django.conf import settings
import libManager.common.util.LoggerManager

if __name__ == '__main__':
    print("BASE_DIR:" + settings.BASE_DIR)
    logger = libManager.common.util.LoggerManager.get_logger()
    logger.debug("debug log")
    logger.info("info log")
    logger.error("error log")
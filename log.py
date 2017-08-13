# coding: utf-8
import logging


logger = logging.getLogger("spider")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

fh = logging.FileHandler('data/spider.log')
fh.setFormatter(formatter)
ch = logging.StreamHandler()
ch.setFormatter(formatter)
ch.setLevel(logging.INFO)

logger.addHandler(fh)
logger.addHandler(ch)

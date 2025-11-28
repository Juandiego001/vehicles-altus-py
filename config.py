import os
import redis
import logging
import logging.config
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

URL_VEHICLE = os.getenv('URL_VEHICLE')
URL_FOR_REQUEST = os.getenv('URL_FOR_REQUEST')
URL_OPENAPI = os.getenv('URL_OPENAPI')
MAIL_RECIPIENTS: str = os.getenv('MAIL_RECIPIENTS')
MAIL_USER = os.getenv('MAIL_USER')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_PORT = os.getenv('MAIL_PORT')
MAIL_SENDER = os.getenv('MAIL_SENDER')
MAIL_SERVER = os.getenv('MAIL_SERVER')

'''Check required folders'''
Path('./logs').mkdir(parents=True, exist_ok=True)

'''Logger config'''
logging.config.fileConfig('log.conf')
access_logger = logging.getLogger('access_logger')
error_logger = logging.getLogger('error_logger')

'''Redis config'''
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

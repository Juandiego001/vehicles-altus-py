from main import main
from utils import validate_env
from config import access_logger, error_logger
from datetime import datetime


if __name__ == '__main__':

    try:
        validate_env()
        today_date = datetime.today()
        date_since = datetime(year=today_date.year, month=today_date.month,
                              day=today_date.day, hour=0, minute=0, second=0)
        date_until = datetime(year=today_date.year, month=today_date.month,
                              day=today_date.day, hour=23, minute=59, second=59)
        access_logger.info(
            f'Starting script with date since: {date_since} and date until: {date_until}')
        main(date_since, date_until)
    except Exception as ex:
        error_logger.exception(f'There was an error: {str(ex)}')

import functools
import inspect
import logging
import random
import time
import re

import pytz
from dateutil.tz import tz
from django.conf import settings
from django.utils import timezone
from django.utils.timezone import is_naive, make_aware
from datetime import timedelta, datetime, tzinfo, date
from datetime import timezone as datetime_timezone

from common.core.enums import ImportErrMsg

logger = logging.getLogger(__name__)


class TimeHelper:
    date_time_format = '%Y-%m-%d %H:%M:%S'
    dateformat = '%Y-%m-%d'
    tz_info = tz.gettz(settings.TIME_ZONE)
    utc_tz_info = datetime_timezone.utc

    def __init__(self):
        super(TimeHelper, self).__init__()

    @classmethod
    def get_date_time_obj(cls, time_input, time_format='%Y-%m-%d %H:%M:%S.%f'):
        time_output = time_input
        if not time_input:
            return time_output

        if type(time_input) == str:
            time_output = datetime.strptime(time_input, time_format)

        if is_naive(time_output):
            time_output = make_aware(time_output, is_dst=True)
        return time_output

    @classmethod
    def local_dt_str_of_timezone_aware_dt(cls, date_time, iso_format: bool = False):
        from dateutil.parser import parse

        if not date_time:
            return date_time

        if type(date_time) == str:
            date_time = parse(date_time)

        t = date_time.astimezone(TimeHelper.tz_info)
        if iso_format:
            t = t.isoformat()
        else:
            t = t.strftime(TimeHelper.date_time_format)
        return t

    @classmethod
    def astimezone(cls, date_time):
        new_date_time = date_time.astimezone(cls.tz_info)
        return new_date_time

    @classmethod
    def get_total_seconds_by_date(cls, dt: date) -> int:
        time_delta = dt + timedelta(days=3) - timezone.localdate()
        seconds = time_delta.total_seconds()
        seconds = max(0, int(seconds))
        return seconds

    @classmethod
    def date_to_datetime(cls, dt: date) -> datetime:
        dt = datetime.combine(dt, datetime.min.time())
        return dt

    @classmethod
    def date_time_threshold(cls):
        cur_date_time = timezone.now()
        date_time_threshold = cur_date_time - timedelta(days=settings.VALID_DAYS)
        return date_time_threshold

    @classmethod
    def to_datetime_from_iso_str(cls, time_str):
        t = datetime.fromisoformat(time_str).astimezone(timezone.utc)
        return t

    @classmethod
    def to_datetime_from_specific_time_format(cls, time_str, time_str_format="%Y-%m-%dT%H:%M:%SZ"):
        t = datetime.strptime(time_str, time_str_format).replace(tzinfo=timezone.utc)
        return t

    @classmethod
    def parse_time_range(cls, time_range):
        err_msg = ImportErrMsg.INVALID_SCHEDULE

        try:
            begin_time_str, end_time_str = [t.strip() for t in time_range.split('-')]
        except ValueError:
            raise ValueError(err_msg)
        except AttributeError:
            raise ValueError(err_msg)

        try:
            begin_time = datetime.strptime(begin_time_str, "%Y/%m/%d %H:%M")
        except ValueError:
            raise ValueError(err_msg)
        try:
            end_time = datetime.strptime(end_time_str, "%Y/%m/%d %H:%M")
        except ValueError:
            try:
                end_time = datetime.strptime(end_time_str, "%H:%M")
                end_time = datetime.combine(begin_time.date(), end_time.time())
            except ValueError:
                raise ValueError(err_msg)
        begin_time = make_aware(begin_time).astimezone(pytz.UTC)
        end_time = make_aware(end_time).astimezone(pytz.UTC)

        if begin_time > end_time:
            raise ValueError(err_msg)

        return begin_time, end_time

    @classmethod
    def parse_date_begin_end_str(cls, begin_time_str, end_time_str):
        err_msg = ImportErrMsg.INVALID_DATE

        try:
            begin_time = datetime.strptime(begin_time_str, "%Y/%m/%d")
        except ValueError:
            raise ValueError(err_msg)
        try:
            end_time = datetime.strptime(end_time_str, "%Y/%m/%d")
        except ValueError:
            raise ValueError(err_msg)

        if begin_time > end_time:
            raise ValueError(err_msg)

        return begin_time, end_time

    @classmethod
    def parse_date_str(cls, time_str, time_format="%Y/%m/%d"):
        if not time_str:
            return time_str
        err_msg = ImportErrMsg.INVALID_FORMAT_DATE
        try:
            result_time = datetime.strptime(time_str, time_format)
        except ValueError:
            raise ValueError(err_msg)
        return result_time

    @classmethod
    def random_time_delay(cls, min_delay=0, max_delay=1):
        random_delay = random.uniform(min_delay, max_delay)
        time.sleep(random_delay)
        print(f"Random time delay of {random_delay:.2f} seconds complete.")

    @classmethod
    def extract_LYYMMDD_date(cls, s):
        # 使用正则表达式提取日期部分
        match = re.match(r'L(\d{2})(\d{2})(\d{2})(\d{2})', s)
        if match:
            # 提取年份、月份和日期
            year = int(match.group(1)) + 2000  # 假设年份是2000年后的
            month = int(match.group(2))
            day = int(match.group(3))

            # 检查月份和日期的合理性
            if 1 <= month <= 12:
                try:
                    date_time = datetime(year, month, day, 10)
                    return date_time
                except ValueError:
                    return None
            else:
                return None
        else:
            return None

    @classmethod
    def parse_excel_date_to_datetime(cls, excel_date):
        if not excel_date:
            return excel_date
        if type(excel_date) in [datetime, date]:
            return excel_date

        excel_date = int(excel_date)
        if excel_date < 60:
            delta = timedelta(days=(excel_date - 1))
        else:
            delta = timedelta(days=(excel_date - 2))
        return datetime(1900, 1, 1) + delta


def timer(func):
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        tic = time.perf_counter()
        value = func(*args, **kwargs)
        toc = time.perf_counter()
        elapsed_time = toc - tic
        logger.info('{}, Elapsed time: {:.4f} seconds'.format(func.__name__, elapsed_time))
        return value

    return wrapper_timer

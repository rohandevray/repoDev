from datetime import datetime, time
from django.utils import timezone
import pytz

utc=pytz.UTC
def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time
    # begin_time.replace(tzinfo=utc)
    # end_time.replace(tzinfo=utc)
    # check_time.replace(tzinfo=utc)
    print(begin_time)
    print(end_time)
    print(check_time)
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time
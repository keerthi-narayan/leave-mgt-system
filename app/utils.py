from datetime import date
from dateutil.relativedelta import relativedelta

def inclusive_days(start: date, end: date) -> int:
    return (end - start).days + 1

def dates_overlap(a_start: date, a_end: date, b_start: date, b_end: date) -> bool:
    return not (a_end < b_start or b_end < a_start)

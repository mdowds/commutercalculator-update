from datetime import datetime


def make_datetime(day):
    return datetime.strptime(day + ' 06 2016', '%d %m %Y')

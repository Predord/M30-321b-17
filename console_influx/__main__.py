from datetime import datetime, timedelta

from .db_req import RequestInflux

DEFAULT_ADDRESS = 'localhost'
DEFAULT_DATABASE = 'dtbs1'
DEFAULT_MEASURE_NAME = 'measurenm'


class AskToExit(Exception):
    pass


def ex_decorator(f):
    def dec():
        try:
            f()
        except AskToExit:
            print('GOOD BYE')
        except Exception:
            print("ERROR IN ARGS")
    return dec


def read_input(default=None):
    k = input()
    if k == '':
        return default
    if k == "exit":
        raise AskToExit
    return k


@ex_decorator
def main():
    print("HELLO HERE")
    while True:
        print("WHATS address is for ur database? Default:", DEFAULT_ADDRESS)
        print("FILL empty if u want to use default, exit to exit")
        RequestInflux.influx_address = read_input(DEFAULT_ADDRESS)
        print("WHATS database name in your influx? Default:", DEFAULT_DATABASE)
        print("FILL empty if u want to use default, exit to exit")
        RequestInflux.database_name = read_input(DEFAULT_DATABASE)
        print("WHATS measure name in your influx database? Default:", DEFAULT_MEASURE_NAME)
        print("FILL empty if u want to use default, exit to exit")
        RequestInflux.measure_name = read_input(DEFAULT_MEASURE_NAME)
        print("WHATS Variables u want to select format a,b,c,d without whitespaces")
        print("FILL empty if u want to find all, exit to exit")
        variable = read_input(None)
        print("WHATS begin time, format d:m:y::h:m:s")
        print("FILL empty if u want to find all, exit to exit")
        a = read_input(None)
        fnd = False
        if a is not None:
            fnd = True
            a = datetime.strptime(a, "%d:%m:%Y::%X") - datetime(1970, 1, 1)
            a_t = int(a / timedelta(microseconds=1) * 1000)
        else:
            a_t = 0
        b = None
        if fnd:
            print("WHATS period u whant to find, format d:h:m:s")
            print("FILL empty if u dont need it, exit to exit")
            b = read_input(None)
            if b is not None:
                date_mas = b.split(':')
                a += timedelta(days=float(date_mas[0]), hours=float(date_mas[1]), minutes=float(date_mas[2]),
                               seconds=float(date_mas[3]))
                b = int(a / timedelta(microseconds=1) * 1000)
        print(RequestInflux.time_request(variable, a_t, b))
        print('TAKES', RequestInflux.time_spent, 'seconds')


main()

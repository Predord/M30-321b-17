import time

from influxdb import InfluxDBClient


class RequestInflux:
    influx_address = ''
    database_name = ''
    measure_name = ''
    time_spent = 0

    @classmethod
    def time_request(cls, variables=None, a=0, b=None):
        if variables is None:
            variables = '*'
        qr = 'SELECT ' + variables + ' FROM ' + cls.measure_name + ' WHERE \"time\" > ' + str(a)
        if b is not None:
            qr += ' AND \"time\" < ' + str(b) + ';'
        print(qr)
        bt = time.time()
        cli = InfluxDBClient(host=cls.influx_address, database=cls.database_name)
        ret_qr = cli.query(qr, epoch='ms')
        cls.time_spent = time.time() - bt
        return list(ret_qr.get_points())

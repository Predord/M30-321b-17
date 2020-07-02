import random
import time

from influxdb import InfluxDBClient

class BD_API:

    def write_points(self, data) -> None:
        pass

    def get_points(self) -> []:
        pass


class BD_API_influx(BD_API):
    def __init__(self, host, db: str, mes_name: str):
        self._db = InfluxDBClient(host=host, port=8086, database=db)
        self._mes_name = mes_name

    def write_points(self, data):
        ret_data = [{
            "measurement": self._mes_name,
            "fields": data
        }]
        self._db.write_points(ret_data)

    def get_points(self):
        rd = self._db.query(
            f"SELECT * FROM \"{self._mes_name}\";",
            epoch="s"
        )
        return [x for x in rd.get_points()]


class Writer:
    def __init__(self, bd_class: BD_API):
        self._per = {}
        self._bd = bd_class

    def set_per(self, nam, val):
        self._per[nam] = val

    def get_per_list(self):
        return [x for x in self._per]

    def write_to_bd(self):
        self._bd.write_points(self._per)


if __name__ == "__main__":
    kt = Writer(BD_API_influx("influxDB", "eldata", "izmerenie"))
    while True:
        for a in "ueiqopasdfg":
            kt.set_per(a, random.randint(0, 20))
        kt.write_to_bd()
        time.sleep(1)
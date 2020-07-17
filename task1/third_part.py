from multiprocessing import Manager, Lock, Process
import random
import time

from flask import Flask, request
from .first_part import Writer, BD_API_influx
from .mqtt_reader import create_mqtt_reader


class glob_vars:
    app = Flask(__name__)
    manager = Manager()
    fields = manager.dict()
    mqtt_fields = manager.dict()
    lock = manager.Lock()
    writer_proc = None
    handler_f = {}
    writer = Writer(BD_API_influx("influxDB", "eldata", "izmerenie1"))


def writer_circle(writer, field, mqtt_fields ,lock):
    while True:
        lock.acquire()
        field_ = dict(field)
        mqtt_field = dict(mqtt_fields)
        for i_iterator in field_:
            t = field_[i_iterator]
            writer.set_per(i_iterator, t)
            t += random.random() * random.randint(-2, 2)
            field[i_iterator] = t
        for i_iterator in mqtt_field:
            writer.set_per(i_iterator, mqtt_field[i_iterator])
        lock.release()
        writer.write_to_bd()
        time.sleep(1)


@glob_vars.app.route("/<cmd>")
def handler(cmd):
    f = glob_vars.handler_f.get(cmd, None)
    if f is None:
        return "NO COMMAND"
    else:
        return f()


def cmd_decor(cmd):
    def decor(f):
        glob_vars.handler_f[cmd] = f
        return f
    return decor


@cmd_decor("list")
def list_f():
    glob_vars.lock.acquire()
    ln = len(glob_vars.fields) + len(glob_vars.mqtt_fields)
    strng = '<p>P_COUNTS = ' + str(ln) + '</p>' + '<p>==================</p>'
    for a in glob_vars.fields:
        strng += '<p>'+ a + ' : ' + str(glob_vars.fields[a]) + '</p>'
    for a in glob_vars.mqtt_fields:
        strng += '<p>' + a + ' : ' + str(glob_vars.mqtt_fields[a]) + '</p>'
    glob_vars.lock.release()
    return strng


@cmd_decor("start")
def start():
    if glob_vars.writer_proc is not None:
        return "Cant start"
    glob_vars.writer_proc = Process(target=writer_circle, args=(glob_vars.writer, glob_vars.fields,
                                                                glob_vars.mqtt_fields, glob_vars.lock,))
    glob_vars.writer_proc.start()
    if glob_vars.writer_proc is None:
        return "ERROR IN CIRCLE"
    return "Started"


@cmd_decor("start_mqtt")
def start_mqtt_proc():
    topic = request.args.get("tpc", None)
    var = request.args.get("var", None)
    if topic is None or var is None:
        return "ERROR IN VALUES"
    ps = Process(target=create_mqtt_reader, args=(topic, var, glob_vars.mqtt_fields, glob_vars.lock, 'mosquitto',))
    ps.start()
    return "OK"


@cmd_decor("stop")
def stop():
    if glob_vars.writer_proc is None:
        return "Not started yet"
    glob_vars.lock.release()
    glob_vars.lock.acquire()
    glob_vars.writer_proc.terminate()
    glob_vars.writer_proc.join()
    glob_vars.lock.release()
    return "Stopped"


@cmd_decor("add")
def add():
    name = request.args.get("name", None)
    try:
        begin_value = float(request.args.get("beg", None))
    except Exception:
        return "Error in values"
    glob_vars.lock.acquire()
    glob_vars.fields[name] = begin_value
    glob_vars.lock.release()
    return "Added " + name + " : " + str(begin_value)


if __name__ == "__main__":
    glob_vars.app.run(host='0.0.0.0', port=7777)

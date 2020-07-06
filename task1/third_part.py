from multiprocessing import Manager, Lock, Process
import random
import time

from flask import Flask, request
from pisar import Writer, BD_API_influx


class glob_vars:
    app = Flask(__name__)
    manager = Manager()
    fields = manager.dict()
    lock = manager.Lock()
    writer_proc = None
    handler_f = {}
    writer = Writer(BD_API_influx("influxDB", "eldata", "izmerenie1"))


def writer_circle(writer, field, lock):
    while True:
        lock.acquire()
        field_ = dict(field)
        for i_iterator in field_:
            t = field_[i_iterator]
            writer.set_per(i_iterator, t)
            t += random.random() * random.randint(-2, 2)
            field[i_iterator] = t
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
    ln = len(glob_vars.fields)
    strng = '<p>P_COUNTS = ' + str(ln) + '</p>' + '<p>==================</p>'
    for a in glob_vars.fields:
        strng += '<p>'+ a + ' : ' + str(glob_vars.fields[a]) + '</p>'
    glob_vars.lock.release()
    return strng


@cmd_decor("start")
def start():
    if glob_vars.writer_proc is not None:
        return "Cant start"
    glob_vars.writer_proc = Process(target=writer_circle, args=[glob_vars.writer, glob_vars.fields,
                                                                glob_vars.lock])
    glob_vars.writer_proc.start()
    if glob_vars.writer_proc is None:
        return "ERROR IN CIRCLE"
    return "Started"


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

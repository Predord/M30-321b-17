from paho.mqtt.client import Client as cli


def write_to_field(variable, value, field, lock):
    lock.acquire()
    field[variable] = value
    lock.release()


def create_mqtt_reader(topic, var, field, lock, mqtt_addr):
    client = cli()
    client.connect(mqtt_addr)

    def on_connect_func(client, userdata, flags, rc):
        client.subscribe(topic+'/'+var)
    client.on_connect = on_connect_func

    def on_message(client, userdata, msg):
        try:
            write_to_field(var, float(msg.payload), field, lock)
        except Exception:
            pass
    client.on_message = on_message
    client.loop_forever()


import PySimpleGUI as sg
from multiprocessing import Process, Queue
import asyncio
from nats.aio.client import Client as NATS


class NATS_CONFIG:
    room_number = 'asd12131451'
    nats_addr = 'nats://127.0.0.1:4222'
    my_name = 'AlenKostik'


class QueuePrimitive:
    def __init__(self):
        self.queue = Queue()


async def nats_init_and_bind(get_queue: QueuePrimitive, send_queue: QueuePrimitive):
    nats = NATS()
    await nats.connect(NATS_CONFIG.nats_addr)

    async def msg_recived(msg):
        get_queue.queue.put(msg.data.decode())

    await nats.subscribe(NATS_CONFIG.room_number, cb=msg_recived)

    while True:
        try:
            txt = send_queue.queue.get(block=False)
            await nats.publish(NATS_CONFIG.room_number, (NATS_CONFIG.my_name+">> "+str(txt)).encode())
        except Exception:
            pass
        await asyncio.sleep(0.1)


def init_nats(get_queue, send_queue):
    asyncio.get_event_loop().run_until_complete(nats_init_and_bind(get_queue, send_queue))


get_queue = QueuePrimitive()
send_queue = QueuePrimitive()

ps = Process(target=init_nats, args=(get_queue, send_queue))
ps.start()

sg.theme('System Default 1')
layout = [
    [sg.Output(size=(80, 20), key='-otpt-')],
    [sg.InputText('', (80, 1), key='-inpt-')],
    [sg.Button('Send', key='-snd-')]
        ]
window = sg.Window('Simple-chat', layout)

while True:
    event, values = window.read(timeout=100)
    if event == 'Cancel' or event == sg.WIN_CLOSED:
        break
    if event == '-snd-':
        if values['-inpt-']:
            window['-inpt-'].Update('')
            send_queue.queue.put(values['-inpt-'])
    try:
        gv = get_queue.queue.get(block=False)
        print(gv)
    except Exception:
        pass

ps.kill()
ps.join()
window.close()

from flask import Flask, jsonify, request
import threading
import pytuya
import secrets

devices = {}

app = Flask(__name__)

def init_devices():
    global devices
    devices_info = secrets.DEVICES_INFO

    for dev_name in devices_info.keys():
        dev_info = devices_info[dev_name]
        devices[dev_name] = pytuya.OutletDevice(dev_info['id'], dev_info['ip'], dev_info['local_key'])

def set(device, value):
    dev = devices[device]
    if value == 'on':
        dev.set_status(True)
    elif value == 'off':
        dev.set_status(False)
    elif value == 'toggle':
        data = dev.status()
        state = data['dps']['1']
        dev.set_status(not state)

@app.route('/')
def action():
    args = request.args
    if 'device' not in args or 'key' not in args or 'value' not in args:
        return jsonify({'status': 'FAIL', 'reason': 'Missing required argument'})

    device = args['device']
    key = args['key']
    value = args['value']

    if not key == secrets.PLUGS_KEY:
        return jsonify({'status': 'FAIL', 'reason': 'Invalid key'})
    
    if device not in devices:
        return jsonify({'status': 'FAIL', 'reason': 'Invalid device'})

    if value not in ['on', 'off', 'toggle']:
        return jsonify({'status': 'FAIL', 'reason': 'Invalid value'})

    threading.Thread(target=set, args=[device, value]).start()
    return jsonify({'status': 'OK'})

if __name__ == '__main__':
    global devices
    devices = plugs.get_devices()
    app.run(port=6661)

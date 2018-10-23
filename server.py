from flask import Flask, jsonify, request
import threading
import pytuya
import secrets

devices = {}
groups = {}

app = Flask(__name__)

def init_devices():
    global devices
    global groups

    groups = secrets.GROUPS
    devices_info = secrets.DEVICES_INFO

    for dev_name in devices_info.keys():
        dev_info = devices_info[dev_name]
        devices[dev_name] = pytuya.OutletDevice(dev_info['id'], dev_info['ip'], dev_info['key'])

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

def get(device):
    dev = devices[device]
    data = dev.status()
    state = data['dps']['1']
    if state: return 'on'
    else: return 'off'

@app.route('/')
def action():
    args = request.args
    if 'device' not in args or 'key' not in args:
        return jsonify({'status': 'FAIL', 'reason': 'Missing required argument'})

    device = args['device']
    key = args['key']

    if not key == secrets.PLUGS_KEY:
        return jsonify({'status': 'FAIL', 'reason': 'Invalid key'})
    
    if device not in devices and device not in groups:
        return jsonify({'status': 'FAIL', 'reason': 'Invalid device'})

    if 'value' in args:
        value = args['value']
        if value not in ['on', 'off', 'toggle']:
            return jsonify({'status': 'FAIL', 'reason': 'Invalid value'})

        if device in groups:
            for d in groups[device]:
                threading.Thread(target=set, args=[d, value]).start()
        else:
            threading.Thread(target=set, args=[device, value]).start()
        return jsonify({'status': 'OK'})
    else:
        value = get(device)
        return jsonify({'status': 'OK', 'value': value})

if __name__ == '__main__':
    init_devices()
    app.run(port=6661)

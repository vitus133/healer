#!/bin/python3
import json, requests
import time
from datetime import datetime

be = '192.168.16.48'

MAX_RETRIES = 3

# Check which cells are available in the BE.
# If a cell is in failed state - restart it up to MAX_RETRIES times
# Each retry is composed from stop and start with their correspondent timeouts
# If stop failed, it also counts towards maximum attempts
# After maximum healing attempts is reached, further healing attempts are prohibited.
# Every cell that reached "Started" state (by manual fixing), if it was prohibited,
#       will be un-prohibited

def get_cell_status(uuid):
    url = 'http://{ip}:8080/api/v1/net-item/{uuid}/status'.format(
            ip=be, uuid=uuid)
    status = json.loads(requests.get(url=url).text)['current_status'].upper()
    return status


def get_cells():
    url = 'http://{ip}:8080/api/v1/net-item/'.format(ip=be)
    resp = json.loads(requests.get(url=url).text)
    rv = {}
    for result in resp['results']:
        rv[result['uuid']] = get_cell_status(result['uuid'])
    return rv        

op_ctl = {
    'stop': {
        'transitional': 'STOPPING',
        'final': 'STOPPED',
        'timeout': 40
    },
    'start': {
        'transitional': 'STARTING',
        'final': 'STARTED',
        'timeout': 300
    }
}
def cell_operation(uuid, operation):
    oper = 'http://{ip}:8080/api/v1/net-item/{uuid}/{op}/'.format(
            ip=be, uuid=uuid, op=operation)
    started = time.time()
    timeout = op_ctl[operation]['timeout']
    print('Initiating cell {id} {op} at {time}, timeout {to}'.format(
        id=uuid.split('-')[0], op=operation, time=datetime.now().ctime(), to=timeout))
    ret = {}
    ret['uuid'] = uuid
    http_resp = requests.post(url=oper, auth=('admin', 'qwer1234'))
    resp = http_resp.status_code
    if resp == 202:
        while time.time() - started < timeout:
            status = get_cell_status(uuid)
            print('Checking cell {id} status: {status} at time {time}'.format(
                id=uuid.split('-')[0], status=status, time=datetime.now().ctime()))
            if status == op_ctl[operation]['transitional']:
                print('Sleeping 10 sec')
                time.sleep(10)
            elif status == 'FAILED':
                ret['result'] = 'failure'
                ret['message'] = 'stratus {op} failed'.format(op=operation)
                return ret
            elif status == op_ctl[operation]['final']:
                ret['result'] = 'success'
                ret['message'] = 'ok'
                return ret
            else:
                ret['result'] = 'failure'
                ret['message'] = 'cell status {status}'.format(status=status)
                return ret

        if time.time() - started >= timeout:
            print('Can\'t {op} net item {uuid} in {sec} seconds'.format(
                op=operation, uuid=uuid.split('-')[0], sec=timeout))
            ret['result'] = 'failure'
            ret['message'] = 'timeout'
            return ret
    else:
        print('Can\'t {op} net item {uuid}, return code {rc} text {text}'.format(
            uuid=uuid.split('-')[0], rc=resp, op=operation, text=http_resp.text) )
        ret['result'] = 'failure'
        ret['message'] = 'http response {rc}'.format(rc=resp)
        time.sleep(30)
        return ret


if __name__ == '__main__':
    prohibited_cells = []
    while(True):
        cells = get_cells()
        for key in cells:
            if key in prohibited_cells:
                phb = ', prohibited'
            else:
                phb = ''
            print('{time} {uuid}, {st}{phb}'.format(
                time=datetime.now().ctime(),
                uuid=key.split('-')[0], 
                st=cells[key], phb=phb ))
            if cells[key] == 'STARTED' and key in prohibited_cells:
                prohibited_cells.remove(key)
            if cells[key] == 'FAILED' and key not in prohibited_cells:
                print('Restarting cell {key}'.format(key=key.split('-')[0]))
                retries = MAX_RETRIES
                while retries > 0:
                    retries -= 1
                    status = cell_operation(key, 'stop')
                    if status['result'] != 'success':
                        print('Stop failed with message \"{message}\". Remained {retries} retries'.format(
                            message=status['message'], retries=retries))
                        continue
                    status = cell_operation(key, 'start')
                    if status['result'] != 'success':
                        print('Start failed with message \"{message}\". Remained {retries} retries'.format(
                            message=status['message'], retries=retries))
                        continue
                    else:
                        print('Successfully recovered cell {key}'.format(key=key.split('-')[0]))
                        break
                if retries <= 0:
                    prohibited_cells.append(key)
                    print('Prohibited cell {uuid} from additional healing attempts'.format(
                        uuid=key.split('-')[0]
                    ))

        time.sleep(30)
        print('---')

#!/usr/bin/env python
# Author: 'JiaChen'

import subprocess


def monitor():
    """监控硬盘容量"""
    shell_command = '/bin/df -Pm | grep "^/dev"'
    status, result = subprocess.getstatusoutput(cmd=shell_command)
    result = result.split('\n')
    if status != 0:
        value_dict = {'status': status}
    else:
        value_dict = {'status': status, 'data': {}}
        for line in result:
            line = line.split()
            mounted_on, size, used, avail, use = line[5], int(line[1]), int(line[2]), int(line[3]), int(line[4].strip('%'))
            value_dict['data'][mounted_on] = {'Size': size, 'Used': used, 'Avail': avail, 'Use': use}
    return value_dict

if __name__ == '__main__':
    print(monitor())
    # {'status': 0, 'data': {'/boot': {'Use': 8, 'Avail': 419, 'Used': 33, 'Size': 477}, '/': {'Use': 5, 'Avail': 43412, 'Used': 1972, 'Size': 47819}}}

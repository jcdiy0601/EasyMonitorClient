#!/usr/bin/env python
# Author: 'JiaChen'

import subprocess


def monitor():
    """监控负载"""
    shell_command = '/usr/bin/uptime'
    status, result = subprocess.getstatusoutput(cmd=shell_command)
    if status != 0:
        value_dict = {'status': status}
    else:
        result = result.split()[-3:]
        load1, load5, load15 = result
        value_dict = {
            'load1': float(load1.strip(',')),
            'load5': float(load5.strip(',')),
            'load15': float(load15.strip(',')),
            'status': status
        }
    return value_dict

if __name__ == '__main__':
    print(monitor())
    # {'status': 0, 'load1': 0.05, 'load5': 0.04, 'load15': 0.05}


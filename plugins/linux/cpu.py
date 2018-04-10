#!/usr/bin/env python
# Author: 'JiaChen'

import subprocess


def monitor():
    """监控cpu"""
    shell_command = '/usr/bin/sar 1 3 | grep "Average\|平均时间"'
    status, result = subprocess.getstatusoutput(cmd=shell_command)
    if status != 0:
        value_dict = {'status': status}
    else:
        user = float(result.split()[2])
        system = float(result.split()[4])
        iowait = float(result.split()[5])
        idle = float(result.split()[-1])
        value_dict = {
            'user': user,
            'system': system,
            'iowait': iowait,
            'idle': idle,
            'status': status
        }
    return value_dict

if __name__ == '__main__':
    print(monitor())
    # {'system': 0.67, 'idle': 99.33, 'status': 0, 'iowait': 0.0, 'user': 0.0}
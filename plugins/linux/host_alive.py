#!/usr/bin/env python
# Author: 'JiaChen'

import subprocess


def monitor():
    """主机存活检测"""
    shell_command = '/usr/bin/uptime'
    status, result = subprocess.getstatusoutput(cmd=shell_command)
    if status != 0:
        value_dict = {'status': status}
    else:
        value_dict = {'uptime': 0, 'status': status}
    return value_dict

if __name__ == '__main__':
    print(monitor())
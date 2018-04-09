#!/usr/bin/env python
# Author: 'JiaChen'

import subprocess


def monitor():
    """监控网卡流量"""
    shell_command = '/usr/bin/sar -n DEV 1 5 | grep -v IFACE | grep "Average\|平均时间"'
    result = subprocess.Popen(shell_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.readlines()


if __name__ == '__main__':
    print(monitor())

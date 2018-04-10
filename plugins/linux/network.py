#!/usr/bin/env python
# Author: 'JiaChen'

import subprocess


def monitor():
    """监控网卡流量"""
    shell_command = '/usr/bin/sar -n DEV 1 5 | grep -v IFACE | grep "Average\|平均时间"'
    status, result = subprocess.getstatusoutput(cmd=shell_command)
    result = result.split('\n')
    if status != 0:
        value_dict = {'status': status}
    else:
        value_dict = {'status': status, 'data': {}}
        for line in result:
            line = line.split()
            nic_name, t_in, t_out = line[1], float(line[4]), float(line[5])
            value_dict['data'][nic_name] = {'t_in': t_in, 't_out': t_out}
    return value_dict

if __name__ == '__main__':
    print(monitor())
    # {'data': {'lo': {'t_out': 0.0, 't_in': 0.0}, 'eth0': {'t_out': 0.01, 't_in': 0.01}}, 'status': 0}
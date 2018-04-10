#!/usr/bin/env python
# Author: 'JiaChen'

import subprocess


def monitor():
    """监控内存"""
    shell_command = "/bin/grep 'MemTotal\|MemFree\|Buffers\|^Cached\|SwapTotal\|SwapFree' /proc/meminfo"
    status, result = subprocess.getstatusoutput(cmd=shell_command)
    if status != 0:
        value_dict = {'status': status}
    else:
        '''
        MemTotal:         493952 kB
        MemFree:          186704 kB
        Buffers:           50576 kB
        Cached:           153364 kB
        SwapTotal:       2031612 kB
        SwapFree:        2031592 kB 
       '''
        value_dict = {'status': status}
        monitor_dict = {
            'MemUsage': 'percentage',
            'SwapUsage': 'percentage'
        }
        for i in result.split('kB\n'):
            key = i.split()[0].strip(':')
            value = int(i.split()[1])
            value_dict[key] = value

        if monitor_dict['SwapUsage'] == 'percentage':
            value_dict['SwapUsage'] = value_dict['SwapTotal'] - value_dict['SwapFree']
            value_dict['SwapUsage_p'] = round(float(value_dict['SwapUsage'] / value_dict['SwapTotal'] * 100), 2)

        if monitor_dict['MemUsage'] == 'percentage':
            value_dict['MemUsage'] = value_dict['MemTotal'] - value_dict['MemFree'] - value_dict['Cached'] - value_dict['Buffers']
            value_dict['MemUsage_p'] = round(float(value_dict['MemUsage'] / value_dict['MemTotal'] * 100), 2)
    return value_dict

if __name__ == '__main__':
    print(monitor())
    # {'Buffers': 59048, 'MemUsage': 112712, 'SwapUsage': 20, 'SwapUsage_p': 0.0, 'status': 0, 'SwapFree': 2031592, 'MemTotal': 493952, 'MemFree': 165884, 'SwapTotal': 2031612, 'Cached': 156308, 'MemUsage_p': 22.82}

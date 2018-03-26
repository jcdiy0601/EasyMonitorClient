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

        # {'SwapFree': 2031592, 'SwapTotal': 2031612, 'Cached': 154364, 'status': 0, 'Buffers': 51728, 'MemFree': 172208, 'MemTotal': 493952}

        if monitor_dict['SwapUsage'] == 'percentage':
            value_dict['SwapUsage'] = value_dict['SwapTotal'] - value_dict['SwapFree']
            value_dict['SwapUsage_p'] = float(value_dict['SwapUsage'] / value_dict['SwapTotal'] * 100)

        if monitor_dict['MemUsage'] == 'percentage':
            value_dict['MemUsage'] = value_dict['MemTotal'] - value_dict['MemFree'] - value_dict['Cached'] - value_dict['Buffers']
            value_dict['MemUsage_p'] = float(value_dict['MemUsage'] / value_dict['MemTotal'] * 100)
    return value_dict

if __name__ == '__main__':
    print(monitor())

#!/usr/bin/env python
# Author: 'JiaChen'

import subprocess


def monitor():
    """监控cpu"""
    shell_command = '/usr/bin/top -bn 1 | grep "^Tasks"'
    status, result = subprocess.getstatusoutput(cmd=shell_command)
    if status != 0:
        value_dict = {'status': status}
    else:
        value_dict = {
            'running': None,
            'sleeping': None,
            'stopped': None,
            'zombie': None,
            'status': status
        }
    temp_list = []
    for item in result.split():
        if item.isdigit():
            temp_list.append(int(item))
    if len(temp_list) == 5:
        value_dict['running'] = temp_list[1]
        value_dict['sleeping'] = temp_list[2]
        value_dict['stopped'] = temp_list[3]
        value_dict['zombie'] = temp_list[4]
    else:
        value_dict['status'] = 1
    return value_dict

if __name__ == '__main__':
    print(monitor())

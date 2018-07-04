#!/usr/bin/env python
# Author: 'JiaChen'

import subprocess


def monitor():
    """监控tomcat 内存"""
    shell_command = '/bin/ps -ef | grep java | grep tomcat | grep -v grep'
    status, result = subprocess.getstatusoutput(cmd=shell_command)
    if status != 0:
        value_dict = {'status': status}
    else:
        pid_list = []
        value_dict = {'status': status, 'data': {}}
        result_list = result.split('\n')
        for item in result_list:
            pid_list.append(item.split()[1])
        shell_command = '/usr/bin/top -bn 1 | grep {pid}'
        for pid in pid_list:
            shell_command = shell_command.format(pid=pid)
            status, result = subprocess.getstatusoutput(cmd=shell_command)
            if status != 0:
                value_dict = {'status': status}
            else:
                value_dict['data'][pid] = {'mem_used': round(float(result.split()[9]), 2)}
    return value_dict

if __name__ == '__main__':
    print(monitor())

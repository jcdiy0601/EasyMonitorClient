#!/usr/bin/env python
# Author: 'JiaChen'

import subprocess


def monitor():
    shell_command = '/usr/bin/sar 1 3 | grep "Average\|平均时间"'

#!/usr/bin/env python
# Author: 'JiaChen'

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from core.main import CommandHandle

if __name__ == '__main__':
    main_obj = CommandHandle(sys.argv)

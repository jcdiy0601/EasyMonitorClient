#!/usr/bin/env python
# Author: 'JiaChen'

import os

# 项目家目录
BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 主机名，要与cmdb客户端中的主机名一致
HOSTNAME = 'CentOS-01_172.16.99.24'

# 获取配置API
CONFIG_API = 'http://127.0.0.1:8000/monitor_api/v1/config'

# 提交数据API
DATA_API = 'http://127.0.0.1:8000/monitor_api/v1/data'

# 用于API认证的KEY
KEY = '299095cc-1330-11e5-b06a-a45e60bec08b'

# 用于API认证的请求头
AUTH_KEY_NAME = 'monitor-api-auth-key'

# 错误日志
ERROR_LOG_FILE = os.path.join(BASEDIR, "logs", 'error.log')

# 运行日志
RUN_LOG_FILE = os.path.join(BASEDIR, "logs", 'run.log')

# 超时时间，秒
REQUEST_TIME_OUT = 30

# 监控配置更新间隔，秒
CONFIG_UPDATE_INTERVAL = 300

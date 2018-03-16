#!/usr/bin/env python
# Author: 'JiaChen'

from conf import settings
import time
import hashlib
import requests
import json
import threading
from plugins import plugin_map


class ClientHandle(object):
    """客户端处理"""
    def __init__(self):
        self.config_api = settings.CONFIG_API   # 获取监控配置api
        self.data_api = settings.DATA_API   # 提交监控数据api
        self.key = settings.KEY     # key
        self.key_name = settings.AUTH_KEY_NAME  # key_name
        self.hostname = settings.HOSTNAME   # 主机名
        self.monitored_services = {}    # 已监控的服务

    def forever_run(self):
        """永久启动客户端监控"""
        exit_flag = False
        config_last_update_time = 0     # 配置监控配置更新的时间，第一次运行初始化时间为0
        while not exit_flag:
            if time.time() - config_last_update_time > settings.CONFIG_UPDATE_INTERVAL:     # 当前时间减上次更新配置时间大于配置文件中设置的监控配置更新间隔
                latest_configs = self.load_latest_config()   # 获取最新的监控配置信息, {'application': {'LinuxNetwork': ['LinuxNetworkPlugin', 60], 'LinuxCpu': ['LinuxCpuPlugin', 30], 'LinuxMemory': ['LinuxMemoryPlugin', 60], 'LinuxLoad': ['LinuxLoadPlugin', 60]}}
                print('加载最新配置--->', latest_configs)
                self.monitored_services.update(latest_configs)  # 更新已监控的服务字典
                print('已监控的服务--->', self.monitored_services)
                config_last_update_time = time.time()   # 重新设置监控配置更新时间
            # 开始监控服务
            for application_name, value in self.monitored_services['application'].items():
                if len(value) == 2:     # 第一次监控,给值[列表]中添加时间
                    self.monitored_services['application'][application_name].append(0)
                monitor_interval = value[1]  # 获取监控间隔
                last_invoke_time = value[2]  # 获取监控调用的最后一次时间
                if time.time() - last_invoke_time > monitor_interval:   # 如果时间大于监控间隔则需要去跑插件了
                    self.monitored_services['application'][application_name][2] = time.time()
                    t = threading.Thread(target=self.invoke_plugin, args=(application_name, value))
                    t.start()
                    print('开始监控[%s]服务' % application_name)
                else:
                    print('开始监控[%s]服务，还差%s秒' % (application_name, monitor_interval - (time.time() - last_invoke_time)))
            time.sleep(1)

    def load_latest_config(self):
        """获取最新的监控配置信息"""
        try:
            headers = {}
            headers.update(self.auth_key())
            data = {'hostname': self.hostname}
            response = requests.get(url=self.config_api, params=data, headers=headers)
        except Exception as e:
            response = str(e)
        return response.json()

    def auth_key(self):
        """生成认证串"""
        ha = hashlib.md5(self.key.encode('utf-8'))
        timestamp = time.time()
        ha.update(bytes('%s|%f' % (self.key, timestamp), encoding='utf-8'))
        encrypt = ha.hexdigest()
        result = '%s|%f' % (encrypt, timestamp)
        return {self.key_name: result}

    def invoke_plugin(self, application_name, value):
        """调用插件"""
        print('调用插件----------------》')
        plugin_name = value[0]
        if hasattr(plugin_map, plugin_name):
            func = getattr(plugin_map, plugin_name)
            plugin_callback = func()
        else:
            print("\033[31;1m没有在plugin_map中找到应用集[%s]插件名为[%s]的函数\033[0m" % (application_name, plugin_name))
#!/usr/bin/env python
# Author: 'JiaChen'

from conf import settings
import time
import hashlib
import requests
import json
import threading
from plugins import plugin_map
from lib.log import Logger


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
        config_last_update_time = 0     # 初始化监控配置更新的时间，第一次运行初始化时间为0
        while not exit_flag:
            if time.time() - config_last_update_time > settings.CONFIG_UPDATE_INTERVAL:     # 当前时间减上次更新配置时间大于配置文件中设置的监控配置更新间隔
                latest_configs = self.get_latest_config()   # 获取最新的监控配置信息, {'application': {'LinuxCpu': ['LinuxCpuPlugin', 30], 'LinuxLoad': ['LinuxLoadPlugin', 60], 'code': xxx, 'message': xxx}
                if latest_configs['code'] == 400:    # 请求api接口失败
                    Logger().log(message='请求获取监控配置API接口失败,%s' % latest_configs['message'], mode=False)
                    time.sleep(60)
                elif latest_configs['code'] == 401:  # api认证失败
                    Logger().log(message='API认证未通过', mode=False)
                    time.sleep(60)
                elif latest_configs['code'] == 404:  # 资源不存在
                    Logger().log(message='资源不存在,%s' % self.hostname, mode=False)
                    time.sleep(60)
                elif latest_configs['code'] == 200:  # 获取最新监控配置成功
                    Logger().log(message=latest_configs['message'], mode=True)
                    self.monitored_services.update(latest_configs['application'])  # 更新已监控的服务字典
                    Logger().log(message='更新监控配置,%s' % self.monitored_services, mode=True)
                    config_last_update_time = time.time()   # 重新设置监控配置更新时间
            if self.monitored_services:
                # {'LinuxCpu': ['LinuxCpuPlugin', 30], 'LinuxNetwork': ['LinuxNetworkPlugin', 60], 'LinuxLoad': ['LinuxLoadPlugin', 60], 'LinuxMemory': ['LinuxMemoryPlugin', 60]}
                # 开始监控服务
                for application_name, value in self.monitored_services.items():
                    if len(value) == 2:     # 第一次监控,给值[列表]中添加时间
                        self.monitored_services[application_name].append(0)
                    monitor_interval = value[1]  # 获取监控间隔
                    last_invoke_time = value[2]  # 获取监控调用的最后一次时间
                    if time.time() - last_invoke_time > monitor_interval:   # 如果时间大于监控间隔则需要去跑插件了
                        self.monitored_services[application_name][2] = time.time()
                        t = threading.Thread(target=self.invoke_plugin, args=(application_name, value))
                        t.start()
                        Logger().log(message='开始监控[%s]服务' % application_name, mode=True)
            #         else:
            #             print('开始监控[%s]服务，还差%s秒' % (application_name, monitor_interval - (time.time() - last_invoke_time)))
                time.sleep(1)

    def get_latest_config(self):
        """获取最新的监控配置信息"""
        try:
            headers = {}
            headers.update(self.auth_key())     # 生成api认证的主机头信息
            payload = {'hostname': self.hostname}   # 将hostname作为参数传递给api
            Logger().log(message='获取最新的监控配置信息', mode=True)
            response = requests.get(url=self.config_api, params=payload, headers=headers)
            return response.json()
        except Exception as e:
            return {'code': 400, 'message': str(e)}

    def post_data(self, data, callback=None):
        """向服务器提交监控数据"""
        status = True
        try:
            headers = {}
            headers.update(self.auth_key())     # 生成api认证的主机头信息
            Logger().log(message='发送监控数据,%s' % data, mode=True)
            response = requests.post(url=self.data_api, json=json.dumps(data), headers=headers)
        except Exception as e:
            response = str(e)
            status = False
        if callback:
            callback(data=data, status=status, response=response)

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
        plugin_name = value[0]
        if hasattr(plugin_map, plugin_name):
            func = getattr(plugin_map, plugin_name)
            try:
                plugin_data = func()    # 执行插件
            except Exception as e:
                Logger().log(message='插件异常,%s' % str(e), mode=False)
                return
            report_data = {
                'hostname': self.hostname,
                'application_name': application_name,
                'data': plugin_data
            }
            self.post_data(data=report_data, callback=self.call_back)
        else:
            Logger().log(message='plugin_map中未找到应用集插件,%s-%s' % (application_name, plugin_name), mode=False)

    def call_back(self, data, status, response):
        """监控数据提交后回调函数"""
        if status:
            response = response.json()
            if response['code'] == 401:
                Logger().log(message='API认证未通过', mode=False)
            elif response['code'] == 404:
                Logger().log(message='资源不存在,%s' % self.hostname, mode=False)
            elif response['code'] == 200:
                Logger().log(message='监控数据发送成功,%s' % data, mode=True)
        else:
            Logger().log(message='请求发送监控数据API接口失败,%s' % response, mode=False)

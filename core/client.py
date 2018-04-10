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
import os
import sys
import atexit
import subprocess
from signal import SIGTERM


class ClientHandle(object):
    """客户端处理"""
    def __init__(self):
        self.config_api = settings.CONFIG_API   # 获取监控配置api
        self.data_api = settings.DATA_API   # 获取提交监控数据api
        self.key = settings.KEY     # key
        self.key_name = settings.AUTH_KEY_NAME  # key_name
        self.hostname = settings.HOSTNAME   # 主机名
        self.monitored_services = {}    # 已监控的服务
        self.pid_file = settings.PID_FILE   # PID文件

    def start_daemonize(self):
        """启动守护进程"""
        print('启动监控客户端...')
        time.sleep(1)
        pid = os.fork()
        # 父进程(会话组头领进程)退出，这意味着一个非会话组头领进程永远不能重新获得控制终端
        if pid > 0:
            sys.exit(0)     # 父进程退出
        # 从母体环境脱离
        os.chdir('/')   # chdir确认进程不保持任何目录于使用状态，否则不能umount一个文件系统，也可以改变到对于守护程序运行重要的文件所在目录
        os.umask(0)     # 调用umask(0)以便拥有对于写的任何东西的完全控制，因为有时不知道继承了什么样的umask
        os.setsid()     # setsid调用成功后，进程成为新的会话组长和新的进程组长，并与原来的登录会话和进程组脱离
        # 执行第二次fork
        pid = os.fork()
        if pid > 0:
            sys.exit(0)     # 第二个父进程退出
        # 进程已经是守护进程了，重定向标准文件描述符
        sys.stdout.flush()
        sys.stderr.flush()
        # dup2函数原子化地关闭和复制文件描述符，重定向到 / dev / nul，即丢弃所有输入输出
        with open('/dev/null') as read_null, open('/dev/null', 'w') as write_null:
            os.dup2(read_null.fileno(), sys.stdin.fileno())
            os.dup2(write_null.fileno(), sys.stdout.fileno())
            os.dup2(write_null.fileno(), sys.stderr.fileno())
        # 写入pid文件
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
        # 开始循环
        self.forever_run()

    def stop_daemonize(self):
        """关闭守护进程"""
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
                os.kill(pid, SIGTERM)
        except Exception as e:
            print('监控客户端未启动')
            sys.exit(1)
        atexit.register(os.remove, self.pid_file)
        print('关闭监控客户端...')
        time.sleep(1)

    def status_daemonize(self):
        """守护进程状态"""
        if os.path.isfile(self.pid_file):
            with open(self.pid_file, 'r') as f:
                pid = f.read().strip()
                shell_command = 'ps -ef | grep -v grep | grep %s' % pid
                result = subprocess.getoutput(shell_command)
                if result:
                    print('监控客户端运行中...')
                else:
                    print('监控客户端已关闭...')
        else:
            print('监控客户端未启动...')

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

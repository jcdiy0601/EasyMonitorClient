#!/usr/bin/env python
# Author: 'JiaChen'

from core.client import ClientHandle
from lib.log import Logger


class CommandHandle(object):
    """命令处理"""
    def __init__(self, sys_args):
        self.sys_args = sys_args
        if len(self.sys_args) != 2:  # 输入参数数量不正确
            self.help_message()     # 执行显示帮助信息方法并退出程序
        self.command_check()    # 执行命令检测方法

    def command_check(self):
        """检查用户输入的命令"""
        if hasattr(self, self.sys_args[1]):     # 通过反射查看是否存在输入命令的方法
            func = getattr(self, self.sys_args[1])
            return func()
        else:
            self.help_message()     # 非start、stop、status则执行显示帮助信息方法并退出程序

    @staticmethod
    def help_message():
        """显示帮助信息并退出程序"""
        valid_commands = '''
执行监控启动程序需要在其后输入相关参数：
        start  启动监控客户端
        stop   关闭监控客户端
        status 监控客户端状态
        '''
        exit(valid_commands)    # 输出提示信息，并退出程序

    @staticmethod
    def start():
        """启动监控客户端"""
        Logger().log(message='启动监控客户端', mode=True)
        client_obj = ClientHandle()
        client_obj.start()

    @staticmethod
    def stop():
        """关闭监控客户端"""
        Logger().log(message='关闭监控客户端', mode=True)
        client_obj = ClientHandle()
        client_obj.stop()

    @staticmethod
    def status():
        """监控客户端状态"""
        client_obj = ClientHandle()
        client_obj.status()

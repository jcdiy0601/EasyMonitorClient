#!/usr/bin/env python
# Author: 'JiaChen'

from core import client


class CommandHandle(object):
    """命令处理"""
    def __init__(self, sys_args):
        self.sys_args = sys_args
        if len(self.sys_args) < 2:  # 没有输入参数
            self.help_message()
        self.command_check()

    def command_check(self):
        """检查用户输入的命令"""
        if hasattr(self, self.sys_args[1]):     # 通过反射查看是否存在输入命令的方法
            func = getattr(self, self.sys_args[1])
            return func()
        else:
            self.help_message()

    @staticmethod
    def help_message():
        """帮助信息"""
        valid_commands = '''
        start 启动监控客户端
        stop  关闭监控客户端
        '''
        exit(valid_commands)

    @staticmethod
    def start():
        """启动监控客户端"""
        client_obj = client.ClientHandle()
        client_obj.forever_run()

    def stop(self):
        """关闭监控客户端"""
        pass

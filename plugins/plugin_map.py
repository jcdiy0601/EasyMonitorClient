#!/usr/bin/env python
# Author: 'JiaChen'

from plugins.linux import cpu, load, memory, network, disk

# 此文件中的函数名要与数据库中应用集的插件名一致


def LinuxCpuPlugin():
    """Linux系统CPU监控插件"""
    return cpu.monitor()


def LinuxLoadPlugin():
    """Linux系统负载监控插件"""
    return load.monitor()


def LinuxMemoryPlugin():
    """Linux系统内存监控插件"""
    return memory.monitor()


def LinuxNetworkPlugin():
    """Linux系统网卡流量监控插件"""
    return network.monitor()

def LinuxDiskPlugin():
    """Linux系统硬盘监控插件"""
    return disk.monitor()


def AgentPingPlugin():
    """"""
    pass
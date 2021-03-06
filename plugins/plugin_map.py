#!/usr/bin/env python
# Author: 'JiaChen'

from plugins.linux import cpu, load, memory, network, disk, process
from plugins.tomcat import tomcat_cpu, tomcat_memory
from plugins import linux, tomcat

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


def LinuxProcessPlugin():
    """Linux系统进程监控插件"""
    return process.monitor()


def TomcatCpuPlugin():
    """Tomcat CPU监控"""
    return tomcat_cpu.monitor()


def TomcatMemoryPlugin():
    """Tomcat 内存监控"""
    return tomcat_memory.monitor()
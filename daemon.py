#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import os
import time
import multiprocessing


class Daemon:
    """
    守护进程
    """

    def __init__(self, proc_name,
                 stdin='/dev/null', stdout='/dev/null',
                 stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.proc_name = proc_name
        self.proc_num = 0
        self.monitor_proc = None
        self.pid_file = '/tmp/{0}.pid'.format(self.proc_name)

    def daemonize(self):
        """
        转变成守护进程
        """
        try:
            pid = os.fork()
            if pid > 0:
                # 退出主进程
                sys.exit(0)
        except OSError, e:
            sys.stderr.write(
                'fork #1 failed: {0} ({1})\n'.format(e.errno, e.strerror))
            sys.exit(1)

        os.chdir("/")
        os.setsid()
        os.umask(0)

        # 创建子进程
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError, e:
            sys.stderr.write(
                'fork #2 failed: {0} ({1})\n'.format(e.errno, e.strerror))
            sys.exit(1)

        # 重定向文件描述符
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # 创建pid_file文件
        pid = str(os.getpid())
        file(self.pid_file, 'w+').write('{0}\n'.format(pid))

    def monitor_work(self):
        """
        监控工作进程
        """
        monitor_pid = os.getpid()
        while True:
            cmd = 'ps axu | grep "{0}" | grep -v "grep" | wc -l'.format(
                self.proc_name)
            proc_num = os.popen(cmd).read().strip()

            # 计算进程数
            if proc_num < self.proc_num:
                self.restart(monitor_pid)
                sys.exit(0)
            elif proc_num > self.proc_num:
                self.proc_num = proc_num

            time.sleep(2)

    def monitor(self):
        """
        开启监控
        """
        self.monitor_proc = multiprocessing.Process(target=self.monitor_work,
                                                    name='monitor')
        self.monitor_proc.start()

    def start(self):
        """
        开启守护进程
        """
        # 检查pid文件是否存在以探测是否存在进程
        try:
            pf = file(self.pid_file, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = 'pid_file {0} already exist. Daemon already running?\n'
            sys.stderr.write(message.format(self.pid_file))
            sys.exit(1)

        self.daemonize()
        self.monitor()
        self.run()

    def stop(self, except_pid=None):
        """
        停止守护进程
        :param except_pid: 不处理的进程ID
        """
        try:
            # 从pid文件中获取pid
            pf = file(self.pid_file, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            # 重启不报错
            return

        if os.path.exists(self.pid_file):
            os.remove(self.pid_file)

        # 杀进程
        try:
            cmd = 'ps axu | grep {0} | grep -v "grep" '.format(self.proc_name)
            if except_pid:
                cmd += '| grep -v "{0}" '.format(except_pid)
            cmd += u'| awk -F" " \'{{print $2}}\' | xargs kill -9'
            os.system(cmd)
        except OSError:
            pass

    def restart(self, except_pid=None):
        """
        重启守护进程
        :param except_pid: 不处理的进程ID
        """
        self.stop(except_pid)
        self.start()

    def run(self):
        pass
